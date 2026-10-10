extends SceneTree
## Presses Play on the title screen like a player (the Z key) and checks that a scene other than the
## title opens. Prints "=== PLAY: <scene>" and exits 1 if nothing opened.
##   godot --headless --path . --script res://tools/check_play.gd
## Part of tools/check.ps1.


func _initialize() -> void:
	_run()


func _run() -> void:
	change_scene_to_file("res://title.tscn")
	for i in 10:
		await process_frame
	var key := InputEventKey.new()
	key.keycode = KEY_Z
	key.pressed = true
	Input.parse_input_event(key)
	for i in 60:
		await process_frame
	var path := current_scene.scene_file_path if current_scene else ""
	print("=== PLAY: ", path if path != "" else "(nothing)")
	quit(0 if path != "" and path != "res://title.tscn" else 1)
