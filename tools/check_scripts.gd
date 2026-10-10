extends SceneTree
## Loads every .gd file in the project, so parse errors show up even in scripts nothing runs yet.
##   godot --headless --path . --script res://tools/check_scripts.gd
## Part of tools/check.ps1.


func _initialize() -> void:
	var paths := _scripts("res://")
	var broken := 0
	for path in paths:
		var s: Script = load(path)
		if s == null or not s.can_instantiate():
			broken += 1
			print("BROKEN ", path)
	print("=== SCRIPTS: %d checked, %d broken" % [paths.size(), broken])
	quit(1 if broken > 0 else 0)


func _scripts(dir: String) -> Array[String]:
	var out: Array[String] = []
	for f in DirAccess.get_files_at(dir):
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))
	for d in DirAccess.get_directories_at(dir):
		if not d.begins_with(".") and d != "build":
			out.append_array(_scripts(dir.path_join(d)))
	return out
