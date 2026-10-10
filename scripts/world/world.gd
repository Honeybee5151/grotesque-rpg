extends Node2D
## The overworld root (scenes/world/world.tscn). It stays loaded for the whole game and owns what
## outlives a map: story flags, key items, the hero's state between battles, the text box, sound and
## fades. Maps are scripts in scripts/world/maps/ that build themselves (see map.gd).
##
## Map events are coroutines that talk through this node:
##     await world.say("Odo", "Ho! The drowned man walks.")
##     var a := await world.ask({"well": "The well"})   # {"g": "nod"}, {"g": "point", "at": "well"}...

const TextBox := preload("res://scripts/world/text_box.gd")
const Sfx := preload("res://scripts/world/sfx.gd")
const BATTLE := "res://scripts/battle/battle.gd"

## What the gesture menu offers, and the caption shown while the hero acts it out.
const GESTURES := [
	{"label": "Nod", "value": "nod", "caption": "He nods."},
	{"label": "Shake", "value": "shake", "caption": "He shakes his head."},
	{"label": "Shrug", "value": "shrug", "caption": "He shrugs."},
	{"label": "Point", "value": "point", "caption": "He points at %s."},
	{"label": "Show", "value": "show", "caption": "He holds up %s."},
	{"label": "Say nothing", "value": "silent", "caption": "He says nothing."},
]

@export var start_map := "hollowell"
@export var start_spawn := "start"

var flags := {}         # story flags
var items := {}         # key items the hero carries: id -> name ("Odo's lantern"). Show offers them.
var hero_state := {}    # the hero between battles, in the battle's hero shape; empty = fresh
var map: Node2D
var box: TextBox
var sfx: Sfx
var busy := 0           # > 0 while an event or a transition runs: the hero stands still

var _cover: ColorRect


func _ready() -> void:
	RenderingServer.set_default_clear_color(Color("#07050d"))
	sfx = Sfx.new()
	add_child(sfx)
	box = TextBox.new()
	box.sfx = sfx
	add_child(box)
	var top := CanvasLayer.new()
	top.layer = 20
	add_child(top)
	_cover = ColorRect.new()
	_cover.size = Vector2(320, 180)
	_cover.color = Color.BLACK
	_cover.mouse_filter = Control.MOUSE_FILTER_IGNORE
	top.add_child(_cover)
	go(start_map, start_spawn)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_M:
		sfx.muted = not sfx.muted


# --------------------------------------------------------------------------------------------
# maps and events
# --------------------------------------------------------------------------------------------

## Leaves the current map (fading out) and arrives on `map_id` at `spawn`.
func go(map_id: String, spawn: String) -> void:
	busy += 1
	if map != null:
		await cover()
		map.queue_free()
		map = null
	box.close()
	map = load("res://scripts/world/maps/%s.gd" % map_id).new()
	map.name = map_id.to_pascal_case()
	map.world = self
	add_child(map)
	move_child(map, 0)
	map.spawn_player(spawn)
	busy -= 1
	run(map.arrive.bind(spawn))


## Runs an event coroutine with the hero held still, then closes the text box.
func run(ev: Callable) -> void:
	busy += 1
	await ev.call()
	busy -= 1
	if busy == 0:
		box.close()


func say(who: String, text: String, pitch := 1.0) -> void:
	await box.say(who, text, pitch)


func narrate(text: String) -> void:
	await box.say("", text)


func caption(text: String, sec := 0.7) -> void:
	await box.caption(text, sec)


func choose(rows: Array, cancelable := false) -> Variant:
	return await box.choose(rows, cancelable)


## The gesture menu. `point_at` maps target ids to how they read in a caption ("the well"); with
## nothing to point at, Point is greyed out, and so is Show while he carries nothing.
## Returns {"g": "nod"|"shake"|"shrug"|"silent"}, {"g": "point", "at": id} or
## {"g": "show", "item": id}, after the hero has acted it out on the map.
func ask(point_at := {}) -> Dictionary:
	while true:
		var rows := []
		for g: Dictionary in GESTURES:
			var r := {"label": g["label"], "value": g["value"]}
			if g["value"] == "point":
				r["enabled"] = not point_at.is_empty()
			elif g["value"] == "show":
				r["enabled"] = not items.is_empty()
			rows.append(r)
		var g: String = await box.choose(rows)
		var answer := {"g": g}
		var what := ""
		if g == "point" or g == "show":
			var src: Dictionary = point_at if g == "point" else items
			var sub := []
			for id: String in src:
				sub.append({"label": String(src[id]).capitalize() if g == "point" else String(src[id]), "value": id})
			var pick: Variant = await box.choose(sub, true)
			if pick == null:
				continue
			answer["at" if g == "point" else "item"] = pick
			what = src[pick]
		await act(answer, what)
		return answer
	return {}


## The hero acts out an answer, with a caption so it reads at a glance.
func act(answer: Dictionary, what := "") -> void:
	var cap := ""
	for g: Dictionary in GESTURES:
		if g["value"] == answer["g"]:
			cap = g["caption"]
	if cap.contains("%s"):
		cap = cap % what
	sfx.play("gesture")
	box.caption(cap, 0.8)
	var icon: Sprite2D = null
	if answer["g"] == "show":
		icon = _float(map.player, "res://art/world/item_%s.png" % answer["item"])
	elif answer["g"] == "silent":
		icon = _float(map.player, "res://art/world/bubble.png")
	await map.player.gesture(answer["g"])
	if icon != null:
		icon.queue_free()
	await get_tree().create_timer(0.15).timeout


## A small picture over someone's head (a held-up item, a speech bubble), above the darkness.
func _float(who: Node2D, path: String) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = load(path)
	s.centered = false
	s.offset = Vector2(-s.texture.get_width() / 2, -s.texture.get_height())
	s.position = Vector2(0, -25)
	s.z_index = 101
	who.add_child(s)
	return s


# --------------------------------------------------------------------------------------------
# battles
# --------------------------------------------------------------------------------------------

## Starts a battle on top of the map and waits for it (the hand-off agreed with fights, see
## docs/world.md). Returns the battle's result; the hero's state carries into the next fight.
func battle(enemy_ids: Array, context := {}) -> Dictionary:
	busy += 1
	if not hero_state.is_empty():
		context["hero"] = hero_state
	sfx.play("swallow")
	await cover(0.6)
	box.close()
	map.hide()
	map.process_mode = Node.PROCESS_MODE_DISABLED
	var result: Dictionary
	if ResourceLoader.exists(BATTLE):
		var b: Node = load(BATTLE).new()
		add_child(b)
		reveal(0.3)
		result = await b.run(enemy_ids, context)
		await cover(0.5)
		b.queue_free()
	else:
		# fights' battle.gd isn't on this branch yet: say so instead of fighting.
		await reveal(0.01)
		await narrate("(The battle with %s goes here once fights' battle.gd is merged.)" % ", ".join(enemy_ids))
		await cover(0.3)
		result = {"outcome": "won", "hero": hero_state, "turns": 0}
	hero_state = result.get("hero", hero_state)
	map.process_mode = Node.PROCESS_MODE_INHERIT
	map.show()
	await reveal(0.5)
	busy -= 1
	return result


# --------------------------------------------------------------------------------------------
# fades
# --------------------------------------------------------------------------------------------

## Fades to black in four hard steps (no smooth gradients).
func cover(sec := 0.4) -> void:
	for i in range(1, 5):
		_cover.color.a = i / 4.0
		await get_tree().create_timer(sec / 4.0).timeout


func reveal(sec := 0.4) -> void:
	for i in range(3, -1, -1):
		_cover.color.a = i / 4.0
		await get_tree().create_timer(sec / 4.0).timeout


func wait(sec: float) -> void:
	await get_tree().create_timer(sec).timeout
