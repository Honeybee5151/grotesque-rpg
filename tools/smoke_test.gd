extends SceneTree
## Headless autoplay of the tutorial fight.
##   godot --headless --path . --script res://tools/smoke_test.gd -- smart [seed=N]
##   godot --headless --path . --script res://tools/smoke_test.gd -- attack
## "attack" mashes Attack (should hit Drained + mercy); "smart" guards after the coil and salves.
## The same seed replays the same fight, and the full battle log is printed, so a refactor can be
## checked line by line against the previous version.

var m: Node
var policy := "smart"
var frames := 0
var turn := 0
var was_open := false
var printed := 0


func _initialize() -> void:
	Engine.time_scale = 8.0
	var rng_seed := 1
	for a in OS.get_cmdline_user_args():
		if a.begins_with("seed="):
			rng_seed = int(a.trim_prefix("seed="))
		else:
			policy = a
	print("--- policy=%s seed=%d" % [policy, rng_seed])
	seed(rng_seed)
	m = load("res://main.tscn").instantiate()
	root.add_child(m)


func _process(_delta: float) -> bool:
	frames += 1
	if frames > 40000:
		print("TIMEOUT")
		return true
	var said: String = "\n".join(m.transcript)
	if "Victory." in said or "Everything goes quiet." in said:
		_flush()
		print("=== RESULT: ", "VICTORY" if "Victory." in said else "DEFEAT",
			" | hero hp=", m.hp, " mp=", m.mp, " drained=", m.drained, " salves=", m.items.get("salve"), " | turns=", turn)
		return true
	if m._menu_open:
		if not was_open:
			was_open = true
			_decide()
	else:
		was_open = false
		m._action("ok")
	return false


func _flush() -> void:
	while printed < m.transcript.size():
		print("  | ", m.transcript[printed])
		printed += 1


func _decide() -> void:
	var first: String = m._menu_items[0]["label"]
	if first == "Attack":
		turn += 1
		_flush()
		print("[turn %d] hp=%d mp=%d drained=%d | host %d%s" % [turn, m.hp, m.mp, m.drained, m.e_hp, " stunned" if m.e_stunned else ""])
		var choice := 0  # attack
		if policy == "smart":
			if "hungry" in " / ".join(m._log_lines):
				choice = 1  # guard
			elif m.drained > 0 and m.hp < 40 and int(m.items.get("salve", 0)) > 0:
				choice = 2  # item
		m._menu_cursor = choice
		m._action("ok")
	else:
		m._menu_cursor = 0  # Salve
		m._action("ok")
