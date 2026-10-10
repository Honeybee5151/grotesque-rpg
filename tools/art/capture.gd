extends SceneTree
## Screenshot a scene exactly as the player sees it: real renderer, window size and integer
## scaling from project.godot. Opens a window for a moment (headless has no renderer).
##   godot --path . --script res://tools/art/capture.gd -- res://title.tscn out.png [frames=40]

var _out := ""
var _frames := 40


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 2:
		printerr("usage: godot --path . --script res://tools/art/capture.gd -- <scene.tscn> <out.png> [frames]")
		quit(1)
		return
	_out = args[1]
	if args.size() > 2:
		_frames = int(args[2])
	root.add_child(load(args[0]).instantiate())


func _process(_delta: float) -> bool:
	if _out == "":
		return true
	_frames -= 1
	if _frames > 0:
		return false
	var img := root.get_texture().get_image()
	var err := img.save_png(_out)
	if err == OK:
		print("captured %dx%d -> %s" % [img.get_width(), img.get_height(), _out])
	else:
		printerr("could not save %s (error %d)" % [_out, err])
	return true
