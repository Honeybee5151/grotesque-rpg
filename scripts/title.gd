extends Node2D
## Title screen: Play / Quit, plus the update status line. An update that finishes downloading
## adds a "Restart to update" entry; you can keep playing meanwhile (it applies on next launch).

const Sprites := preload("res://scripts/sprite_factory.gd")
const Updater := preload("res://scripts/updater.gd")

var items: Array = []        # {label, id}
var cursor := 0
var rows: Array[Label] = []
var panel: Panel
var arrow: Polygon2D
var status_label: Label
var updater: Node


func _ready() -> void:
	RenderingServer.set_default_clear_color(Color("#07050d"))
	_build_scene()
	items = [{"label": "PLAY", "id": "play"}, {"label": "Quit", "id": "quit"}]
	_rebuild_menu()

	updater = Updater.new()
	add_child(updater)
	updater.enabled = not OS.has_feature("editor") or OS.get_environment("GRP_FORCE_UPDATES") == "1"
	updater.status.connect(_on_status)
	updater.update_ready.connect(_on_update_ready)
	_version_label.text = "v%s" % updater.current_version
	updater.check()


var _version_label: Label


func _build_scene() -> void:
	var bg := Sprite2D.new()
	bg.texture = ImageTexture.create_from_image(Sprites.build_background())
	bg.centered = false
	add_child(bg)

	var frog := Sprite2D.new()
	frog.texture = ImageTexture.create_from_image(Sprites.build_frog(false))
	frog.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	frog.scale = Vector2(2, 2)
	frog.position = Vector2(160, 64)
	add_child(frog)

	var title := _label(Vector2(8, 6), Vector2(100, 40), 14, Color("#e8d55a"))
	title.text = "GROTESQUE\nRPG"
	title.add_theme_color_override("font_outline_color", Color("#2a0818"))
	title.add_theme_constant_override("outline_size", 3)
	var sub := _label(Vector2(8, 40), Vector2(100, 12), 7, Color("#8a82b0"))
	sub.text = "work in progress"
	_version_label = _label(Vector2(240, 4), Vector2(76, 10), 7, Color("#6a6488"))
	_version_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT

	panel = Panel.new()
	panel.position = Vector2(110, 126)
	panel.size = Vector2(100, 42)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.05, 0.035, 0.12, 0.92)
	sb.border_color = Color("#d6d0ff")
	sb.set_border_width_all(1)
	sb.set_corner_radius_all(2)
	panel.add_theme_stylebox_override("panel", sb)
	add_child(panel)

	arrow = Polygon2D.new()
	arrow.polygon = PackedVector2Array([Vector2(0, 0), Vector2(0, 8), Vector2(6, 4)])
	arrow.color = Color("#e8d55a")
	panel.add_child(arrow)
	var tw := create_tween().set_loops()
	tw.tween_property(arrow, "offset:x", 1.5, 0.45)
	tw.tween_property(arrow, "offset:x", 0.0, 0.45)

	status_label = _label(Vector2(0, 169), Vector2(320, 10), 7, Color("#8a82b0"))
	status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER


func _label(pos: Vector2, sz: Vector2, font_size: int, col: Color) -> Label:
	var l := Label.new()
	l.position = pos
	l.size = sz
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", col)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l


func _rebuild_menu() -> void:
	for r in rows:
		r.queue_free()
	rows.clear()
	panel.size.y = 8 + items.size() * 12
	for i in items.size():
		var r := Label.new()
		r.text = items[i]["label"]
		r.position = Vector2(18, 4 + i * 12)
		r.size = Vector2(78, 12)
		r.add_theme_font_size_override("font_size", 10 if i == 0 else 8)
		r.mouse_filter = Control.MOUSE_FILTER_STOP
		r.mouse_entered.connect(_set_cursor.bind(i))
		r.gui_input.connect(_on_row_gui.bind(i))
		panel.add_child(r)
		rows.append(r)
	cursor = clampi(cursor, 0, items.size() - 1)
	_refresh()


func _refresh() -> void:
	arrow.position = Vector2(7, 5 + cursor * 12)
	for i in rows.size():
		rows[i].add_theme_color_override("font_color", Color.WHITE if i == cursor else Color("#9a92c0"))


func _set_cursor(i: int) -> void:
	cursor = i
	_refresh()


func _on_row_gui(event: InputEvent, i: int) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		cursor = i
		_activate()


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	match event.keycode:
		KEY_UP, KEY_W:
			cursor = (cursor - 1 + items.size()) % items.size()
			_refresh()
		KEY_DOWN, KEY_S:
			cursor = (cursor + 1) % items.size()
			_refresh()
		KEY_Z, KEY_ENTER, KEY_KP_ENTER, KEY_SPACE:
			_activate()


func _activate() -> void:
	match str(items[cursor]["id"]):
		"play":
			get_tree().change_scene_to_file("res://main.tscn")
		"restart":
			updater.restart_game()
		"quit":
			get_tree().quit()


func _on_status(text: String) -> void:
	status_label.text = text
	var col := Color("#8a82b0")
	if text.begins_with("Update v") and text.contains("ready"):
		col = Color("#7dff8c")
	elif text.contains("fail") or text.contains("corrupt") or text.contains("Couldn't"):
		col = Color("#ffb070")
	status_label.add_theme_color_override("font_color", col)


func _on_update_ready(_version: String) -> void:
	if items.size() > 0 and items[0]["id"] == "play" and not items.any(func(it): return it["id"] == "restart"):
		items.insert(1, {"label": "Restart to update", "id": "restart"})
		_rebuild_menu()
