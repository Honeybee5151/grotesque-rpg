extends SceneTree
## Dev driver for the overworld: loads the world, plays a script of key presses and waits, and saves
## screenshots. Run with a window (not --headless) to get pictures:
##   godot --path . --script res://scripts/world/dev/drive.gd -- OUT_DIR "R*6 U*4 shot:a Z wait:1 ..."
## Steps: <Key>*n holds a direction for n tiles (U D L R), Z / X press a button, wait:<sec>,
## shot:<name> saves OUT_DIR/<name>.png, pick:<n> moves a menu cursor n down and confirms,
## until:<text> waits until the text box shows text containing <text> (max 20 s).

var world: Node
var out_dir := ""
var steps: PackedStringArray = []
var _i := 0
var _wait := 0.0
var _hold := ""
var _hold_left := 0.0
var _until := ""
var _until_t := 0.0

const DIRS := {"U": KEY_UP, "D": KEY_DOWN, "L": KEY_LEFT, "R": KEY_RIGHT}


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	out_dir = args[0] if args.size() > 0 else "user://"
	steps = (args[1] if args.size() > 1 else "wait:2 shot:start").split(" ", false)
	world = load("res://scenes/world/world.tscn").instantiate()
	root.add_child(world)


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
