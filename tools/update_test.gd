extends SceneTree
## Headless updater tests. Driven by tools/update_test.sh, which serves a fake GitHub release.
##   godot --headless --path . --script res://tools/update_test.gd -- download|apply|clean
## Env: GRP_TEST_API = URL of the fake "latest release" JSON, GRP_FORCE_UPDATES=1.

func _initialize() -> void:
	_run()


func _run() -> void:
	await process_frame
	await process_frame
	var mode := "download"
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		mode = args[0]
	var code := 0
	match mode:
		"clean":
			for p in ["user://update.pck", "user://update.pck.part", "user://update.json"]:
				if FileAccess.file_exists(p):
					DirAccess.remove_absolute(ProjectSettings.globalize_path(p))
			print("cleaned")
		"download":
			var u: Node = load("res://scripts/updater.gd").new()
			root.add_child(u)
			u.enabled = true
			u.api_url_override = OS.get_environment("GRP_TEST_API")
			u.status.connect(func(t: String) -> void: print("  status: ", t))
			await u.check()
			print("RESULT staged=[%s] ready=[%s] current=[%s]" % [u.staged_version(), u.ready_version, u.current_version])
		"apply":
			var boot: Node = load("res://scripts/boot.gd").new()
			print("before: ", _version())
			var applied: bool = boot.apply_pending_update()
			print("applied=", applied, " after: ", _version())
		"semver":
			var U: GDScript = load("res://scripts/updater.gd")
			var cases := [["0.2.0", "0.1.0", true], ["0.1.0", "0.1.0", false], ["0.1.9", "0.2.0", false],
				["1.0.0", "0.9.9", true], ["v0.10.0", "0.9.0", true], ["0.2.0-beta", "0.1.0", true]]
			for c in cases:
				var got: bool = U.is_newer(c[0], c[1])
				print("is_newer(%s, %s) = %s %s" % [c[0], c[1], got, "ok" if got == c[2] else "WRONG"])
				if got != c[2]:
					code = 1
	quit(code)


func _version() -> String:
	var cfg := ConfigFile.new()
	cfg.load("res://release.cfg")
	return str(cfg.get_value("release", "version", "?"))
