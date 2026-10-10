extends SceneTree
## Headless autoplay of battles, for regression and balance checks.
##   godot --headless --path . --script res://tools/smoke_test.gd -- smart
##   godot --headless --path . --script res://tools/smoke_test.gd -- attack runs=200
## Policies: "smart" guards when an enemy telegraphs and salves when Drained and low (no skills);
## "skills" plays smart and saves Crush for a stunned enemy, Mends when low;
## "spam" Crushes whenever it can afford to, otherwise attacks;
## "save" plays to free the Host's man: it never lands a blow that could kill outside a stun, and
## Crushes the stun; "learner" plays like "skills" but misses the first telegraph (it only starts
## guarding once it has been Drained); "thin" focuses the weakest enemy and Crushes whenever that
## kills (a pack's answer), never guarding; "expert" answers each telegraph the way its enemy
## teaches (Guard a guard_blocks move, Crush a breakable inhale, thin a pack), Crushes the stun;
## "attack" only ever attacks: it always gets Drained, and in the tutorial mercy (1 HP floor)
## catches it now and then -- the summary counts how often.
## Any policy aims at a stunned enemy when it has a choice, then a telegraphing one, then the weakest.
## Options: seed=N (first seed, default 1); runs=N (battles on seeds N, N+1, ..., then a balance
## summary); troop=host,host (enemy ids); log=1/0 (every line of every battle, default: on for a
## single battle). The same seed replays the same fight, so a refactor can be diffed line by line.

const Data := preload("res://scripts/data.gd")
const Battle := preload("res://scripts/battle/battle.gd")
const MAX_FRAMES := 3000  # per battle (a tutorial fight takes ~100); past it: TIMEOUT

var policy := "smart"
var first_seed := 1
var runs := 1
var troop: Array = ["host"]
var verbose := true
var battle: Battle
var turn := 0
var printed := 0
var seen_menu := 0
var want := ""  # the row to pick in the submenu the last command opens (item or skill)
var frames := 0
var lowest_hp := 0
var most_drained := 0
var done := false


func _initialize() -> void:
	Engine.time_scale = 8.0
	var log_flag := ""
	for a in OS.get_cmdline_user_args():
		var kv := a.split("=")
		match kv[0]:
			"seed": first_seed = int(kv[1])
			"runs": runs = int(kv[1])
			"troop": troop = Array(kv[1].split(","))
			"log": log_flag = kv[1]
			_: policy = a
	verbose = log_flag == "1" or (log_flag == "" and runs == 1)
	_run_all()


func _process(_delta: float) -> bool:
	if done:
		return true
	if battle == null or battle.view == null:
		return false
	frames += 1
	if frames > MAX_FRAMES:
		print("TIMEOUT")
		quit(1)
		return true
	lowest_hp = mini(lowest_hp, battle.hero.hp)
	most_drained = maxi(most_drained, battle.hero.stacks("drained"))
	var v := battle.view
	if v.menu_open:
		if v.menu_serial != seen_menu:
			seen_menu = v.menu_serial
			_decide()
	else:
		v.action("ok")
	return false


func _run_all() -> void:
	await process_frame  # the root joins the tree only after _initialize
	var results: Array = []
	for i in runs:
		results.append(await _run_one(first_seed + i))
	if runs > 1:
		_summary(results)
	await create_timer(0.3, true, false, true).timeout  # let the last sounds stop before exit
	done = true


func _run_one(s: int) -> Dictionary:
	if verbose:
		print("--- policy=%s seed=%d" % [policy, s])
	seed(s)
	turn = 0
	printed = 0
	frames = 0
	seen_menu = 0
	lowest_hp = Data.HERO["max_hp"]
	most_drained = 0
	battle = Battle.new()
	root.add_child(battle)
	var r: Dictionary = await battle.run(troop)
	_flush()
	var outcome: String = {"won": "VICTORY", "lost": "DEFEAT", "fled": "FLED"}[r["outcome"]]
	var salves: int = battle.items.get("salve", 0)
	var raised: Array = r["flags"].keys()
	print("=== RESULT: %s | hero hp=%d mp=%d drained=%d salves=%d | turns=%d%s" % [
		outcome, battle.hero.hp, battle.hero.mp, battle.hero.stacks("drained"), salves, turn,
		(" | flags=" + ",".join(raised)) if not raised.is_empty() else ""])
	var row := {"won": r["outcome"] == "won", "turns": turn, "hp": battle.hero.hp, "frames": frames,
		"mp": battle.hero.mp, "flags": raised,
		"lowest": lowest_hp, "drained": most_drained,
		"salves": int(Data.ITEMS["salve"]["start"]) - salves}
	battle.queue_free()
	battle = null
	return row


func _flush() -> void:
	if not verbose:
		return
	var said: Array[String] = battle.view.transcript
	while printed < said.size():
		print("  | ", said[printed])
		printed += 1


func _decide() -> void:
	var v := battle.view
	var first: Variant = v.menu_items[0]["value"]
	if first is String and first == "attack":
		turn += 1
		_flush()
		var h := battle.hero
		if verbose:
			var foes: Array[String] = []
			for e in battle.enemies:
				foes.append("%s %d%s" % [e.id, e.hp, " stunned" if e.stacks("stunned") > 0 else ""])
			print("[turn %d] hp=%d mp=%d drained=%d | %s" % [turn, h.hp, h.mp, h.stacks("drained"), ", ".join(foes)])
		var choice := _choose().split(":")
		want = choice[1] if choice.size() > 1 else ""
		_pick(choice[0])
	elif first is String:
		_pick(want)  # the item or skill menu
	else:
		# A target menu: a stunned enemy if there is one, then a telegraphing one, then the weakest.
		v.menu_cursor = 0
		for i in v.menu_items.size():
			if _rank(v.menu_items[i]["value"]) < _rank(v.menu_items[v.menu_cursor]["value"]):
				v.menu_cursor = i
		v.action("ok")


func _rank(e) -> float:
	return (0.0 if e.stacks("stunned") > 0 else 2000.0) + (0.0 if e.telegraphing else 1000.0) + e.hp


# "attack", "guard", "item:salve", "skill:crush"...
func _choose() -> String:
	var h := battle.hero
	var telegraph := battle.enemies.any(func(e) -> bool: return e.alive() and e.telegraphing)
	var stunned := battle.enemies.any(func(e) -> bool: return e.alive() and e.stacks("stunned") > 0)
	var salves: int = battle.items.get("salve", 0)
	match policy:
		"smart", "skills", "learner":
			if telegraph and (policy != "learner" or most_drained > 0):
				return "guard"
			if policy != "smart" and stunned and _affords("crush"):
				return "skill:crush"
			if policy != "smart" and h.hp < 25 and _affords("mend"):
				return "skill:mend"
			if h.stacks("drained") > 0 and h.hp < 40 and salves > 0:
				return "item:salve"
		"spam":
			if _affords("crush"):
				return "skill:crush"
		"thin":
			var crush := roundi(Data.HERO["atk"] * h.atk_mult() * float(Data.SKILLS["crush"]["power"]))
			if _affords("crush") and battle.enemies.any(func(e) -> bool: return e.alive() and e.hp <= crush):
				return "skill:crush"
			if h.stacks("drained") > 1 and salves > 0:
				return "item:salve"
		"expert":
			for e in battle.enemies:
				if e.alive() and e.telegraphing:
					if "crush" in e.data.get("break", {}).get("by", []) and _affords("crush"):
						return "skill:crush"
					var nxt: String = e.data["pattern"][e.ai_step % e.data["pattern"].size()]
					if Data.SKILLS[nxt].get("guard_blocks", false):
						return "guard"
			if stunned and _affords("crush"):
				return "skill:crush"
			var hit := roundi(Data.HERO["atk"] * h.atk_mult() * float(Data.SKILLS["crush"]["power"]))
			if battle.enemies.size() > 1 and _affords("crush") and battle.enemies.any(func(e) -> bool: return e.alive() and e.hp <= hit):
				return "skill:crush"
			if h.stacks("drained") > 1 and salves > 0:
				return "item:salve"
		"save":
			if telegraph:
				return "guard"
			if stunned:
				return "skill:crush" if _affords("crush") else "attack"
			# An attack rolls at most ATK x 1.15, x 1.5 on a crit: hold back while that could kill.
			var reach := ceili(Data.HERO["atk"] * (1.0 + Data.RULES["variance"]) * Data.RULES["crit_mult"])
			if battle.enemies.any(func(e) -> bool: return e.alive() and e.hp <= reach):
				return "guard"
	return "attack"


func _affords(skill: String) -> bool:
	return skill in battle.hero.skills and battle.hero.mp >= int(Data.SKILLS[skill].get("mp", 0))


func _pick(value: String) -> void:
	var v := battle.view
	for i in v.menu_items.size():
		if v.menu_items[i]["value"] == value:
			if not v.menu_items[i].get("enabled", true):
				push_error("menu row '%s' is disabled" % value)
			v.menu_cursor = i
			v.action("ok")
			return
	push_error("no menu row '%s'" % value)


func _summary(rows: Array) -> void:
	var won := rows.filter(func(r) -> bool: return r["won"]).size()
	print("=== SUMMARY: %s vs %s, %d battles (seeds %d-%d), min/avg/max" % [
		policy, ",".join(troop), rows.size(), first_seed, first_seed + rows.size() - 1])
	var floored := rows.filter(func(r) -> bool: return r["lowest"] <= 1).size()
	print("won %d/%d | turns %s | hp left %s | lowest hp %s | most drained %s | salves used %s" % [
		won, rows.size(), _spread(rows, "turns"), _spread(rows, "hp"), _spread(rows, "lowest"),
		_spread(rows, "drained"), _spread(rows, "salves")])
	print("mp left %s" % _spread(rows, "mp"))
	var freed := rows.filter(func(r) -> bool: return "freed" in r["flags"]).size()
	print("freed (killed while stunned) in %d/%d" % [freed, rows.size()])
	print("down to 1 HP (mercy's floor, if on) in %d/%d" % [floored, rows.size()])
	print("frames per battle %s" % _spread(rows, "frames"))


func _spread(rows: Array, key: String) -> String:
	var lo: int = rows[0][key]
	var hi: int = rows[0][key]
	var sum := 0.0
	for r in rows:
		lo = mini(lo, r[key])
		hi = maxi(hi, r[key])
		sum += r[key]
	return "%d/%.1f/%d" % [lo, sum / rows.size(), hi]
