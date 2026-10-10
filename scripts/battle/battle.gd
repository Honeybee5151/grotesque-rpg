extends CanvasLayer
## One battle: the hero against 1-3 enemies, classic front view, turn based. Start one with
##   var battle = preload("res://scripts/battle/battle.gd").new()
##   add_child(battle)
##   var result: Dictionary = await battle.run(["host"], context)
##   battle.queue_free()
## context, all optional: intro (lines replacing the first enemy's own), bg ("cave"),
##   can_run (false), mercy (default: on if an enemy's data asks for it),
##   hero {hp, mp, items, states, skills} carried in from outside (default: fresh).
## result: {outcome: "won" | "lost" | "fled", hero: {hp, mp, items, states}, turns, flags}.
##   flags: story flags the fight raised, e.g. {"freed": true} when the Host dies stunned.
## The battle draws on its own layer over whatever is underneath and keeps running while that
## is paused or disabled. The rules are in docs/combat.md; numbers and lines in scripts/data.gd.
## Flow: run -> intro -> (_round: command phase, enemies decide, everyone acts by speed,
## end of round)* -> the outcome.

const Data := preload("res://scripts/data.gd")
const Battler := preload("res://scripts/battle/battler.gd")
const EnemyAI := preload("res://scripts/battle/enemy_ai.gd")
const BattleView := preload("res://scripts/battle/battle_view.gd")

var hero: Battler
var enemies: Array = []       # Battlers, left to right
var items: Dictionary = {}    # item id -> count
var mercy := false            # the hero can't drop below 1 HP
var can_run := false
var turn := 0
var outcome := ""             # "won", "lost" or "fled" once it's over
var flags: Dictionary = {}    # story flags raised in the fight (an enemy's "death_when")
var _acts: Array = []         # this round's actions in turn order (for chorus moves)
var _chorus_said: Dictionary = {}  # chorus skills whose lines were said this round
var _states_landed: Dictionary = {}  # "states_once" skills that already landed their states
var view: BattleView


func _init() -> void:
	layer = 10
	process_mode = Node.PROCESS_MODE_ALWAYS


func run(enemy_ids: Array, context: Dictionary = {}) -> Dictionary:
	if not is_inside_tree():
		await tree_entered
	var carry: Dictionary = context.get("hero", {})
	hero = Battler.new().setup_hero(carry)
	for id in Data.ITEMS:
		items[id] = Data.ITEMS[id]["start"]
	if carry.has("items"):
		items = Dictionary(carry["items"]).duplicate()
	for id in enemy_ids:
		enemies.append(Battler.new().setup_enemy(id))
	_tell_apart()
	mercy = context.get("mercy", enemies.any(func(e: Battler) -> bool: return e.data.get("mercy", false)))
	can_run = context.get("can_run", false)
	view = BattleView.new()
	add_child(view)
	view.build(context.get("bg", "cave"), hero, enemies)

	for line in context.get("intro", enemies[0].data.get("intro", [])):
		await _say(line)
	while outcome == "":
		await _round()

	var keep := {}
	for s in hero.states:
		if not Data.STATES[s].get("ends_with_battle", false):
			keep[s] = hero.states[s]
	return {
		"outcome": outcome,
		"hero": {"hp": hero.hp, "mp": hero.mp, "items": items.duplicate(), "states": keep},
		"turns": turn,
		"flags": flags.duplicate(),
	}


# ======================================================================================
# Rounds
# ======================================================================================

func _round() -> void:
	turn += 1
	hero.guarding = false
	for e in enemies:
		e.guarding = false
	var acts: Array = [await _command_phase()]
	for e in enemies:
		if e.alive():
			acts.append({"user": e, "skill": EnemyAI.decide(e)})
	for i in acts.size():
		acts[i]["order"] = i
	acts.sort_custom(_sooner)
	_acts = acts
	_chorus_said.clear()
	_states_landed.clear()
	for act in acts:
		if act["user"].alive():
			await _perform(act)
			await _settle()
			if outcome != "":
				return
	await _end_of_round()
	await _settle()


# Turn order: priority moves (Guard) first, then the faster battler; a tie keeps the hero
# ahead of the enemies, and the enemies left to right.
func _sooner(a: Dictionary, b: Dictionary) -> bool:
	var pa := _priority(a)
	var pb := _priority(b)
	if pa != pb:
		return pa > pb
	var ua: Battler = a["user"]
	var ub: Battler = b["user"]
	if ua.agi != ub.agi:
		return ua.agi > ub.agi
	return a["order"] < b["order"]


func _priority(act: Dictionary) -> int:
	if act.has("run"):
		return 1
	if act.has("skill"):
		return Data.SKILLS[act["skill"]].get("priority", 0)
	return 0


func _command_phase() -> Dictionary:
	while true:
		var cmd: Variant = await view.menu([
			{"label": "Attack", "value": "attack"},
			{"label": "Skill", "value": "skill", "enabled": not hero.skills.is_empty()},
			{"label": "Guard", "value": "guard"},
			{"label": "Item", "value": "item"},
			{"label": "Run", "value": "run", "enabled": can_run},
		])
		if cmd == "item":
			var id: Variant = await _item_menu()
			if id != null:
				return {"user": hero, "item": id}
			continue
		if cmd == "run":
			return {"user": hero, "run": true}
		if cmd == "skill":
			cmd = await _skill_menu()
			if cmd == null:
				continue
		var target: Variant = hero
		if Data.SKILLS[cmd].get("target", "enemy") != "self":
			target = await _pick_enemy()
		if target != null:
			return {"user": hero, "skill": cmd, "target": target}
	return {}


# One enemy standing: that one. Several: the player picks; cancel goes back to the commands.
func _pick_enemy() -> Variant:
	var standing := enemies.filter(func(e: Battler) -> bool: return e.alive())
	if standing.size() == 1:
		return standing[0]
	var rows: Array = []
	for e in standing:
		rows.append({"label": _cap(e.name), "value": e})
	var picked: Variant = await view.menu(rows, true, view.select_enemy)
	view.select_enemy(null)
	return picked


func _skill_menu() -> Variant:
	var rows: Array = []
	for id in hero.skills:
		var sk: Dictionary = Data.SKILLS[id]
		rows.append({
			"label": "%s  %d MP" % [sk["name"], sk.get("mp", 0)],
			"value": id,
			"enabled": _can_use(hero, sk),
		})
	return await view.menu(rows, true)


# Enough MP for it, and a healing move only when there's something to heal.
func _can_use(b: Battler, sk: Dictionary) -> bool:
	if b.mp < int(sk.get("mp", 0)):
		return false
	return not sk.has("heal") or b.hp < b.max_hp


func _item_menu() -> Variant:
	var rows: Array = []
	for id in Data.ITEMS:
		var it: Dictionary = Data.ITEMS[id]
		var have: int = items.get(id, 0)
		rows.append({
			"label": "%s x%d" % [it["name"], have],
			"value": id,
			"enabled": have > 0 and _item_helps(hero, it),
		})
	return await view.menu(rows, true)


func _item_helps(b: Battler, it: Dictionary) -> bool:
	if int(it.get("heal", 0)) > 0 and b.hp < b.max_hp:
		return true
	for s in it.get("cures", []):
		if b.stacks(s) > 0:
			return true
	return false


func _perform(act: Dictionary) -> void:
	var user: Battler = act["user"]
	if user.skips_turn():
		await _lose_turn(user)
	elif act.has("item"):
		await _use_item(user, act["item"])
	elif act.has("run"):
		for line in Data.TEXT["flee"]:
			await _say(line)
		outcome = "fled"
	else:
		await _use_skill(user, act["skill"], act.get("target", hero))


# After every action: clear away the fallen, then see whether the battle is over.
func _settle() -> void:
	if outcome != "":
		return
	for e in enemies:
		if not e.alive() and not e.gone:
			e.gone = true
			var lines: Array = e.data.get("death", [])
			var when: Dictionary = e.data.get("death_when", {})
			for s in when:
				if e.stacks(s) > 0:
					lines = when[s]["lines"]
					flags[when[s]["flag"]] = true
					break
			await view.kill_enemy(e)
			for line in lines:
				await _say(line, {"user": e})
			e.states.clear()
	if enemies.all(func(e: Battler) -> bool: return not e.alive()):
		for s in hero.states.keys():
			if Data.STATES[s].get("ends_with_battle", false):
				hero.states.erase(s)
		view.refresh_status(hero)
		for line in Data.TEXT["victory"]:
			await _say(line)
		outcome = "won"
	elif not hero.alive():
		for line in Data.TEXT["defeat"]:
			await _say(line)
		outcome = "lost"


# States tick (Drained bleeds HP and MP), and stuns that ate a turn this round wear off.
func _end_of_round() -> void:
	for b in [hero] + enemies:
		if not b.alive():
			continue
		for s in b.states.keys():
			var st: Dictionary = Data.STATES[s]
			if st.has("tick_hp") or st.has("tick_mp"):
				await _tick(b, s, st)
		if b.lost_turn:
			b.lost_turn = false
			for s in b.states.keys():
				if Data.STATES[s].get("skip_turn", false):
					b.states.erase(s)
			_update_pose(b)


# ======================================================================================
# Actions
# ======================================================================================

func _use_skill(user: Battler, id: String, target: Battler) -> void:
	var sk: Dictionary = Data.SKILLS[id]
	if not target.alive():
		var standing := enemies.filter(func(e: Battler) -> bool: return e.alive())
		if standing.is_empty():
			return
		target = standing[0]
	var vars := {"user": user, "target": target}
	var cost: int = sk.get("mp", 0)
	if user.mp < cost:
		for line in Data.TEXT["no_mp"]:
			await _say(line, vars)
		return
	user.mp -= cost
	view.refresh_status(hero)
	var lines: Array = sk.get("lines", [])
	var movers: Array = [user]
	if sk.get("chorus", false):
		movers = _chorus(id)
		if _chorus_said.has(id):
			lines = []
		elif movers.size() == 1:
			lines = sk.get("lines_alone", lines)
		_chorus_said[id] = true
	for line in lines:
		await _say(line, vars, movers)
	if sk.get("guard", false):
		user.guarding = true
	if sk.has("power") or sk.has("dmg"):
		await _strike(user, target, id, vars)
	if sk.has("heal"):
		var healed := _heal(target, int(sk["heal"]))
		await _say(_fill(Data.TEXT["heal"], {"heal": healed}))
	user.telegraphing = sk.get("telegraph", false)
	_update_pose(user)


func _strike(user: Battler, target: Battler, id: String, vars: Dictionary) -> void:
	var sk: Dictionary = Data.SKILLS[id]
	if target.guarding and sk.get("guard_blocks", false):
		for line in sk.get("blocked", []):
			await _say(line, vars)
		var onto_user: Dictionary = sk.get("blocked_user_states", {})
		for s in onto_user:
			await _add_state(user, s, onto_user[s])
		return
	var r: Dictionary = Data.RULES
	var d: int
	if sk.has("power"):
		var v: float = sk.get("variance", r["variance"])
		d = roundi(float(user.atk) * user.atk_mult() * float(sk["power"]) * randf_range(1.0 - v, 1.0 + v))
	else:
		d = randi_range(sk["dmg"][0], sk["dmg"][1])
	d -= target.def
	var crit: bool = sk.get("crit", false) and randf() < float(r["crit_chance"])
	if crit:
		d = roundi(d * float(r["crit_mult"]))
	var line: String = sk["crit_hit"] if crit and sk.has("crit_hit") else sk.get("hit", "")
	var exposed := false
	for s in target.states:
		if Data.STATES[s].has("damage_taken"):
			d = roundi(d * float(Data.STATES[s]["damage_taken"]))
			line = _state_text(target, s, "hit", line)
			exposed = true
	d = maxi(int(r["min_damage"]), d)
	var guarded := target.guarding
	if guarded:
		d = ceili(d * float(r["guard_mult"]))
	vars["dmg"] = _hurt(target, d, crit or exposed)
	if line != "":
		await _say(_fill(line, vars) + (Data.TEXT["guarded"] if guarded else ""))
	if sk.get("states_once", false):
		if _states_landed.has(id):
			return
		_states_landed[id] = true
	var onto_target: Dictionary = sk.get("states", {})
	for s in onto_target:
		await _add_state(target, s, onto_target[s])


# Takes the hit and shows it. Returns the number for the log: the whole hit on an enemy, the HP
# actually lost on the hero (mercy can soften it).
func _hurt(b: Battler, d: int, big: bool = false) -> int:
	if not b.is_hero:
		b.hp = maxi(0, b.hp - d)
		view.hit_enemy(b, d, big)
		return d
	var before := b.hp
	b.hp = maxi(1 if mercy else 0, b.hp - d)
	var lost := before - b.hp
	view.hurt_hero(lost)
	view.refresh_status(hero)
	return lost


func _use_item(user: Battler, id: String) -> void:
	var it: Dictionary = Data.ITEMS[id]
	items[id] = int(items[id]) - 1
	var cured: Array[String] = []
	for s in it.get("cures", []):
		if user.stacks(s) > 0:
			cured.append(s)
			user.states.erase(s)
	var healed := _heal(user, int(it.get("heal", 0)))
	for line in it.get("lines", []):
		await _say(line, {"user": user})
	var parts: Array[String] = []
	if it.has("heal"):
		parts.append(_fill(Data.TEXT["heal"], {"heal": healed}))
	for s in cured:
		parts.append(Data.STATES[s]["cure"])
	if not parts.is_empty():
		await _say(" ".join(parts))


# Heals up to max HP and shows it; returns how much it healed.
func _heal(b: Battler, amount: int) -> int:
	var healed := mini(amount, b.max_hp - b.hp)
	b.hp += healed
	view.refresh_status(hero)
	if healed > 0 and b.is_hero:
		view.popup_hero("+%d" % healed, Color("#7dff8c"))
	elif healed > 0:
		view.popup_enemy(b, "+%d" % healed, Color("#7dff8c"))
	return healed


# ======================================================================================
# States
# ======================================================================================

func _add_state(b: Battler, s: String, n: int) -> void:
	var st: Dictionary = Data.STATES[s]
	b.states[s] = mini(int(st.get("max_stacks", 1)), b.stacks(s) + n)
	view.refresh_status(hero)
	_update_pose(b)
	for line in _state_text(b, s, "apply", []):
		await _say(line, {"name": b, "stacks": b.states[s]})


func _tick(b: Battler, s: String, st: Dictionary) -> void:
	var n: int = b.states[s]
	var before := b.hp
	b.hp = maxi(1 if mercy and b.is_hero else 0, b.hp - n * int(st.get("tick_hp", 0)))
	var lost := before - b.hp
	var mp_loss := mini(b.mp, n * int(st.get("tick_mp", 0)))
	b.mp -= mp_loss
	if b.is_hero:
		view.popup_hero("-%d" % lost, Color("#ff9ab8"))
	else:
		view.popup_enemy(b, "-%d" % lost, Color("#ff9ab8"))
	view.refresh_status(hero)
	for line in _state_text(b, s, "tick", []):
		await _say(line, {"name": b, "hp": lost, "mp": mp_loss, "stacks": n})


# A skip_turn state eats the action; it wears off at the end of the round.
func _lose_turn(b: Battler) -> void:
	b.lost_turn = true
	if not b.is_hero:
		EnemyAI.lost_turn(b)
	for s in b.states:
		if Data.STATES[s].get("skip_turn", false):
			for line in _state_text(b, s, "skip", []):
				await _say(line, {"name": b})
			return


# A state's lines (key: "apply", "hit", "skip", "tick"), or the holder's own version of them.
func _state_text(b: Battler, s: String, key: String, fallback: Variant) -> Variant:
	var own: Dictionary = b.data.get("state_text", {}).get(s, {})
	return own.get(key, Data.STATES[s].get(key, fallback))


func _update_pose(b: Battler) -> void:
	if b.is_hero or b.gone:
		return
	if b.skips_turn():
		view.set_pose(b, "stunned")
	elif b.telegraphing:
		view.set_pose(b, "telegraph")
	else:
		view.set_pose(b, "normal")


# ======================================================================================
# Text
# ======================================================================================

# Everyone standing who uses this chorus skill this round, so the line moves them all at once.
func _chorus(id: String) -> Array:
	var movers: Array = []
	for act in _acts:
		var u: Battler = act["user"]
		if act.get("skill", "") == id and u.alive() and not u.skips_turn():
			movers.append(u)
	return movers


# Says one line of battle text (see the format at the top of scripts/data.gd). Cues fire as
# the line starts; pose/flash/shake act on the enemy using the skill or holding the state (or on
# every mover of a chorus).
func _say(line: Variant, vars: Dictionary = {}, movers: Array = []) -> void:
	var cue: Dictionary = line if line is Dictionary else {"say": line}
	if movers.is_empty():
		movers = [vars.get("user", vars.get("name"))]
	if cue.has("sfx"):
		view.sfx(cue["sfx"])
	if cue.has("pop"):
		view.hero_gestures(cue["pop"])
	for who in movers:
		if who is Battler and not who.is_hero and not who.gone:
			if cue.has("pose"):
				view.set_pose(who, cue["pose"])
			if cue.has("flash"):
				view.flash_enemy(who, Color(cue["flash"]))
			if cue.has("shake"):
				view.shake_enemy(who)
	await view.say(_fill(cue["say"], vars), cue.get("hold", BattleView.HOLD))


# {user} -> "the Host", {User} -> "The Host"; numbers as they are.
func _fill(text: String, vars: Dictionary) -> String:
	var out := text.replace("{hero}", hero.name)
	for k in vars:
		var v: Variant = vars[k]
		var s: String = v.name if v is Battler else str(v)
		out = out.replace("{%s}" % k, s).replace("{%s}" % _cap(k), _cap(s))
	return out


func _cap(s: String) -> String:
	return s.left(1).to_upper() + s.substr(1)


# Two of the same enemy become "the Grub A" and "the Grub B".
func _tell_apart() -> void:
	var total := {}
	for e in enemies:
		total[e.id] = total.get(e.id, 0) + 1
	var seen := {}
	for e in enemies:
		if total[e.id] > 1:
			var n: int = seen.get(e.id, 0)
			e.name += " " + "ABC"[n]
			seen[e.id] = n + 1
