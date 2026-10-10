extends SceneTree
## Dev driver for the overworld: loads the world, plays a script of key presses and waits, and saves
## screenshots. Run with a window (not --headless) to get pictures:
##   godot --path . --script res://scripts/world/dev/drive.gd -- OUT_DIR "R*6 U*4 shot:a Z wait:1 ..." [START]
## START (optional) jumps in: "map:spawn:flag,key=value,+item,..." e.g. "well_cave:shaft:odo_down,rope_cut".
## Steps: <Key>*n holds a direction for n tiles (U D L R), Z / X press a button, wait:<sec>,
## shot:<name> saves OUT_DIR/<name>.png (skipped headless), pick:<n> moves a menu cursor n down and
## confirms, until:<text> waits until the text box shows text containing <text> (max 20 s; "_" is a
## space), mash:<n> presses Z n times a third of a second apart, fight waits for a battle to start and
## presses Z through it (always the first command) until the map is back, expect:<flag>=<value>
## checks a story flag, expect:scene=<name> checks the current scene's file name, dump prints state.
## For sweeping every answer: call:<method> runs a map event directly, to:<text> goes on through lines
## (Z, first choice in menus) until the box shows <text>, answer:<g>[:<target or item>] picks a
## gesture in the open menu with real key presses, settle goes on until the hero has control again
## or the game is back at the title - and fails as "stuck" if that never happens.
## world_test.gd runs fixed scenarios through this headless and fails on any miss.

const DIRS := {"U": KEY_UP, "D": KEY_DOWN, "L": KEY_LEFT, "R": KEY_RIGHT}

var world: Node
var out_dir := ""
var steps: PackedStringArray = []
var failures: Array[String] = []
var _i := 0
var _wait := 0.0
var _hold := ""
var _hold_ticks := 0     # physics ticks left on a held direction (walking is per tick, so holds are too)
var _until := ""
var _until_t := 0.0
var _mash := 0
var _fight := 0          # 1: waiting for the battle, 2: in it
var _fight_t := 0.0
var _drive := ""         # "to", "answer" or "settle" while one of those steps runs
var _drive_arg := ""
var _drive_t := 0.0
var _drive_sub := ""     # answer: the target/item still to pick in the sub-menu


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	out_dir = args[0] if args.size() > 0 else "user://"
	begin(args[1] if args.size() > 1 else "wait:2 shot:start", args[2] if args.size() > 2 else "")


## Starts a fresh world (optionally jumping in at `start`) and plays `script`.
func begin(script: String, start := "") -> void:
	steps = script.split(" ", false)
	_i = 0
	_wait = 0.0
	_hold = ""
	_until = ""
	_mash = 0
	_fight = 0
	world = load("res://scenes/world/world.tscn").instantiate()
	if start != "":
		var parts := start.split(":")
		world.start_map = parts[0]
		world.start_spawn = parts[1]
		if parts.size() > 2:
			for f in parts[2].split(",", false):
				if f.begins_with("+"):
					world.items[f.substr(1)] = f.substr(1).capitalize()
				elif f.contains("="):
					world.flags[f.get_slice("=", 0)] = f.get_slice("=", 1)
				else:
					world.flags[f] = true
	root.add_child(world)
	current_scene = world


## All steps played. Return true to quit.
func finished() -> bool:
	print("drive: done")
	return true


func _process(delta: float) -> bool:
	if _hold != "":
		return false
	if _until != "":
		_until_t += delta
		var box: Node = world.box if is_instance_valid(world) else null
		if box != null and box._text.text.contains(_until) and box._state in ["wait", "menu"]:
			_until = ""
		elif _until_t > 20.0:
			failures.append("until timed out: '%s' (box: %s)" % [_until, box._text.text if box else "-"])
			print(failures.back())
			_until = ""
		else:
			return false
	if _wait > 0.0:
		_wait -= delta
		return false
	if _fight > 0:
		_fight_t += delta
		var hidden: bool = is_instance_valid(world) and world.map != null and not world.map.visible
		if _fight == 1 and (hidden or _fight_t > 30.0):
			_fight = 2
		elif _fight == 2 and not hidden:
			_fight = 0
			_wait = 0.8
			print("fight: over after %.1f s" % _fight_t)
		elif _fight == 2 and fmod(_fight_t, 0.3) < delta:
			_tap(KEY_Z)
		return false
	if _drive != "":
		_drive_t += delta
		return _drive_step()
	if _mash > 0:
		_mash -= 1
		_tap(KEY_Z)
		_wait = 0.33
		return false
	if _i >= steps.size():
		return finished()
	var s := steps[_i]
	_i += 1
	if s.begins_with("wait:"):
		_wait = float(s.substr(5))
	elif s.begins_with("shot:"):
		if DisplayServer.get_name() != "headless":
			root.get_texture().get_image().save_png(out_dir.path_join(s.substr(5) + ".png"))
	elif s.begins_with("until:"):
		_until = s.substr(6).replace("_", " ")
		_until_t = 0.0
	elif s.begins_with("pick:"):
		for k in int(s.substr(5)):
			_tap(KEY_DOWN)
		_tap(KEY_Z)
		_wait = 0.1
	elif s.begins_with("expect:"):
		_expect(s.substr(7))
	elif s == "dump":
		print("dump: flags=", world.flags, " items=", world.items, " busy=", world.busy,
			" map=", world.map.name if world.map else "-", " hero=", world.hero_state,
			" at=", world.map.player.cell if world.map and world.map.player else "-",
			" held=", Input.is_key_pressed(KEY_RIGHT), " fps=", Engine.get_frames_per_second())
	elif s.begins_with("call:"):
		world.run(Callable(world.map, s.substr(5)))
	elif s.begins_with("to:") or s.begins_with("answer:") or s == "settle":
		var parts := s.split(":", true, 1)
		_drive = parts[0]
		_drive_arg = parts[1].replace("_", " ") if parts.size() > 1 else ""
		_drive_sub = ""
		_drive_t = 0.0
		if _drive == "answer" and _drive_arg.contains(":"):
			_drive_sub = _drive_arg.get_slice(":", 1)
			_drive_arg = _drive_arg.get_slice(":", 0)
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
		_hold_ticks = int(parts[1]) * 16 - 1
		_press(DIRS[_hold])
	return false


func _physics_process(_delta: float) -> bool:
	if _hold != "":
		_hold_ticks -= 1
		if _hold_ticks <= 0:
			_release(DIRS[_hold])
			_hold = ""
	return false


# One frame of a to / answer / settle step. Presses go through real input, so a box that stops
# listening shows up as "stuck".
func _drive_step() -> bool:
	var on_world := is_instance_valid(world) and current_scene == world
	if not on_world:
		if _drive != "settle":
			failures.append("%s '%s': left the world" % [_drive, _drive_arg])
		_drive = ""
		return false
	var box: Node = world.box
	var state: String = box._state
	if _drive_t > 40.0:
		failures.append("stuck in %s '%s': box=%s text='%s' busy=%d" % [
			_drive, _drive_arg, state, box._text.text, world.busy])
		print(failures.back())
		_drive = ""
		return false
	match _drive:
		"to":
			if state in ["wait", "menu"] and box._text.text.contains(_drive_arg):
				_drive = ""
			else:
				_go_on(state)
		"settle":
			if world.busy == 0 and state == "":
				_drive = ""
			else:
				_go_on(state)
		"answer":
			if state == "wait":
				_tap(KEY_Z)
				_wait = 0.05
			elif state == "menu":
				var want := _drive_sub if _drive_arg == "" else _drive_arg
				var target := -1
				for i in box._items.size():
					if String(box._items[i]["value"]) == want:
						target = i
				if target < 0:
					failures.append("answer '%s': not in the menu %s" % [want, box._items])
					print(failures.back())
					_drive = ""
					return false
				if not box._enabled(target):
					failures.append("answer '%s': greyed out" % want)
					print(failures.back())
					_drive = ""
					return false
				var c: int = box._cursor
				var n := 0
				while c != target and n < 20:
					c = (c + 1) % box._items.size()
					while not box._enabled(c):
						c = (c + 1) % box._items.size()
					n += 1
				for k in n:
					_tap(KEY_DOWN)
				_tap(KEY_Z)
				_wait = 0.1
				if _drive_arg != "" and _drive_sub != "":
					_drive_arg = ""          # next: the target / item in the sub-menu
				else:
					_drive = ""
	return false


# Goes on through whatever the box is doing: Z on a finished line, the first choice in a menu.
func _go_on(state: String) -> void:
	if state in ["wait", "menu", "typing", "picture"]:
		_tap(KEY_Z)
		_wait = 0.06


func _expect(spec: String) -> void:
	var kv := spec.split("=")
	var got := ""
	if kv[0] == "scene":
		got = current_scene.scene_file_path.get_file().get_basename() if current_scene else "-"
	elif is_instance_valid(world):
		got = str(world.flags.get(kv[0], "-"))
	if got != kv[1]:
		failures.append("expected %s=%s, got %s" % [kv[0], kv[1], got])
		print(failures.back())


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
