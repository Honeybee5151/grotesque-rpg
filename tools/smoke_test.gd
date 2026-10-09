extends SceneTree
## Headless autoplay of the tutorial fight.
##   godot --headless --path . --script res://tools/smoke_test.gd -- smart
##   godot --headless --path . --script res://tools/smoke_test.gd -- attack
## "attack" mashes Attack (should hit Drained + mercy); "smart" guards after the coil and salves.

var m: Node
var policy := "smart"
var frames := 0
var turn := 0
var was_open := false
var done := false


func _initialize() -> void:
	Engine.time_scale = 8.0
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		policy = args[0]
	m = load("res://main.tscn").instantiate()
	root.add_child(m)


func _process(_delta: float) -> bool:
	frames += 1
	if frames > 40000:
		print("TIMEOUT")
		return true
	var log_text: String = "\n".join(m._log_lines)
	if "Victory." in log_text or "Everything goes quiet." in log_text:
		print("=== RESULT: ", "VICTORY" if "Victory." in log_text else "DEFEAT",
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


func _decide() -> void:
	var first: String = m._menu_items[0]["label"]
	var last_line: String = m._log_lines.back() if m._log_lines.size() > 0 else ""
	if first == "Attack":
		turn += 1
		var all_log: String = " / ".join(m._log_lines)
		print("[turn %d] hp=%d mp=%d drained=%d frog_hp=%d stunned=%s | %s" % [turn, m.hp, m.mp, m.drained, m.e_hp, m.e_stunned, all_log])
		var choice := 0  # attack
		if policy == "smart":
			if "hungry" in all_log:
				choice = 1  # guard
			elif m.drained > 0 and m.hp < 40 and int(m.items.get("salve", 0)) > 0:
				choice = 2  # item
		m._menu_cursor = choice
		m._action("ok")
	else:
		m._menu_cursor = 0  # Salve
		m._action("ok")
