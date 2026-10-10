extends SceneTree
## Dev driver for the overworld: loads the world, plays a script of key presses and waits, and saves
## screenshots. Run with a window (not --headless) to get pictures:
##   godot --path . --script res://scripts/world/dev/drive.gd -- OUT_DIR "R*6 U*4 shot:a Z wait:1 ..." [START]
## START (optional) jumps in: "map:spawn:flag,flag,+item,..." e.g. "well_cave:shaft:odo_down,rope_cut".
## Steps: <Key>*n holds a direction for n tiles (U D L R), Z / X press a button, wait:<sec>,
## shot:<name> saves OUT_DIR/<name>.png, pick:<n> moves a menu cursor n down and confirms,
## until:<text> waits until the text box shows text containing <text> (max 20 s),
## mash:<n> presses Z n times, a third of a second apart; fight waits for a battle to start and
## presses Z through it (always the first command: Attack) until the map is back.

var world: Node
var out_dir := ""
var steps: PackedStringArray = []
var _i := 0
var _wait := 0.0
var _hold := ""
var _hold_left := 0.0
var _until := ""
var _until_t := 0.0
var _mash := 0
var _fight := 0          # 1: waiting for the battle, 2: in it
var _fight_t := 0.0

const DIRS := {"U": KEY_UP, "D": KEY_DOWN, "L": KEY_LEFT, "R": KEY_RIGHT}


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	out_dir = args[0] if args.size() > 0 else "user://"
	steps = (args[1] if args.size() > 1 else "wait:2 shot:start").split(" ", false)
	world = load("res://scenes/world/world.tscn").instantiate()
	if args.size() > 2:
		var start := args[2].split(":")
		world.start_map = start[0]
		world.start_spawn = start[1]
		if start.size() > 2:
			for f in start[2].split(",", false):
				if f.begins_with("+"):
					world.items[f.substr(1)] = f.substr(1).capitalize()
				else:
					world.flags[f] = true
	root.add_child(world)
	current_scene = world


func _process(delta: float) -> bool:
	if _hold != "":
		_hold_left -= delta
		if _hold_left <= 0.0:
			_release(DIRS[_hold])
			_hold = ""
		return false
	if _until != "":
		_until_t += delta
		if world.box._text.text.contains(_until) and world.box._state in ["wait", "menu"]:
			_until = ""
		elif _until_t > 20.0:
			print("until timed out: ", _until, " | box: ", world.box._text.text)
			_until = ""
		else:
			return false
	if _wait > 0.0:
		_wait -= delta
		return false
	if _fight > 0:
		_fight_t += delta
		var hidden: bool = world.map != null and not world.map.visible
		if _fight == 1 and (hidden or _fight_t > 30.0):
			_fight = 2
		elif _fight == 2 and not hidden:
			_fight = 0
			_wait = 0.8
			print("fight: over after %.1f s" % _fight_t)
		elif _fight == 2 and fmod(_fight_t, 0.3) < delta:
			_tap(KEY_Z)
		return false
	if _mash > 0:
		_mash -= 1
		_tap(KEY_Z)
		_wait = 0.33
		return false
	if _i >= steps.size():
		print("drive: done")
		return true
	var s := steps[_i]
	_i += 1
	print("step: ", s)
	if s.begins_with("wait:"):
		_wait = float(s.substr(5))
	elif s.begins_with("shot:"):
		var img := root.get_texture().get_image()
		img.save_png(out_dir.path_join(s.substr(5) + ".png"))
	elif s.begins_with("until:"):
		_until = s.substr(6).replace("_", " ")
		_until_t = 0.0
	elif s.begins_with("pick:"):
		for k in int(s.substr(5)):
			_tap(KEY_DOWN)
		_tap(KEY_Z)
		_wait = 0.1
	elif s == "dump":
		var kids: Array[String] = []
		for k in world.get_children():
			kids.append("%s(%s)" % [k.name, k.get_class()])
		print("dump: flags=", world.flags, " items=", world.items, " busy=", world.busy,
			" map=", world.map.name if world.map else "-", " visible=", world.map.visible if world.map else false,
			" hero=", world.hero_state, " kids=", kids)
	elif s == "fight":
		_fight = 1
		_fight_t = 0.0
	elif s.begins_with("mash:"):
		_mash = int(s.substr(5))
	elif s == "Z" or s == "X":
		_tap(KEY_Z if s == "Z" else KEY_X)
		_wait = 0.1
	elif s.contains("*"):
		var parts := s.split("*")
		_hold = parts[0]
		_hold_left = int(parts[1]) * 16.0 / 60.0 - 0.02
		_press(DIRS[_hold])
	return false


func _tap(k: Key) -> void:
	_press(k)
	_release(k)


func _press(k: Key) -> void:
	var e := InputEventKey.new()
	e.keycode = k
	e.physical_keycode = k
	e.pressed = true
	Input.parse_input_event(e)


func _release(k: Key) -> void:
	var e := InputEventKey.new()
	e.keycode = k
	e.physical_keycode = k
	e.pressed = false
	Input.parse_input_event(e)
