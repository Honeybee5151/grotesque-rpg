extends CanvasLayer
## The overworld's text box: a name tab, a typewriter and pop-up menus. Same windows as the battle,
## so the two screens feel like one game. Z / Enter / Space / left click go on; X / Esc / right click
## back out of a menu that allows it.

signal _done(value: Variant)

const BOX_POS := Vector2(0, 128)
const BOX_SIZE := Vector2(320, 52)
const NARRATION := Color("#b8b0e0")

var sfx: Node

var _panel: Panel
var _text: Label
var _tab: Panel
var _tab_label: Label
var _more: Polygon2D
var _menu: Panel
var _rows: Array[Label] = []
var _items: Array = []
var _cursor := 0
var _cancelable := false
var _state := ""          # "" | "typing" | "wait" | "caption" | "menu"
var _skip := false


func _ready() -> void:
	layer = 30   # above the world's fades, so narration can play over black
	_panel = _window(BOX_POS, BOX_SIZE)
	_text = _label(_panel, Vector2(8, 4), Vector2(304, 44))
	_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_text.visible_characters_behavior = TextServer.VC_CHARS_AFTER_SHAPING
	_tab = _window(Vector2(4, 116), Vector2(60, 13))
	_tab_label = _label(_tab, Vector2(5, 0), Vector2(56, 12))
	_more = Polygon2D.new()
	_more.polygon = PackedVector2Array([Vector2(0, 0), Vector2(6, 0), Vector2(3, 3)])
	_more.position = Vector2(307, 44)
	_more.color = Color("#d6d0ff")
	_panel.add_child(_more)
	var tw := create_tween().set_loops()
	tw.tween_property(_more, "position:y", 45.0, 0.3)
	tw.tween_property(_more, "position:y", 44.0, 0.3)
	_menu = _window(Vector2.ZERO, Vector2(70, 20))
	close()


## Shows a line and waits for the player to go on. An empty `who` is narration.
func say(who: String, text: String, pitch := 1.0) -> void:
	_open(who)
	_text.text = text
	_text.visible_characters = 0
	_state = "typing"
	_skip = false
	var n := 0
	while n < text.length() and not _skip:
		n += 1
		_text.visible_characters = n
		if n % 3 == 1 and text[n - 1] != " ":
			sfx.play("blip", pitch)
		await get_tree().process_frame
	_text.visible_characters = -1
	_state = "wait"
	_more.show()
	await _done
	_more.hide()
	_state = ""


## A line that goes on by itself (the hero's gestures, small beats).
func caption(text: String, sec := 0.7) -> void:
	_open("")
	_text.text = text
	_text.visible_characters = -1
	_state = "caption"
	await get_tree().create_timer(sec).timeout
	_state = ""


## Pops up a menu above the box. rows: [{label, value, enabled?}]. Returns the picked value, or null
## when cancelled (only if `cancelable`). The box keeps showing whatever was said last.
func choose(rows: Array, cancelable := false) -> Variant:
	for r in _rows:
		r.queue_free()
	_rows.clear()
	_items = rows
	_cancelable = cancelable
	var widest := 0
	for it: Dictionary in rows:
		widest = maxi(widest, String(it["label"]).length())
	var w := maxi(60, widest * 5 + 18)
	var h := 8 + rows.size() * 11
	_menu.size = Vector2(w, h)
	_menu.position = Vector2(320 - w - 4, BOX_POS.y - h - 3)
	for i in rows.size():
		var row := _label(_menu, Vector2(5, 4 + i * 11), Vector2(w - 8, 11))
		row.mouse_filter = Control.MOUSE_FILTER_STOP
		row.mouse_entered.connect(_hover.bind(i))
		row.gui_input.connect(_row_gui.bind(i))
		_rows.append(row)
	_cursor = 0
	if not _enabled(0):
		_move(1)
	_refresh_menu()
	_menu.show()
	_state = "menu"
	var v: Variant = await _done
	_menu.hide()
	_state = ""
	return v


func close() -> void:
	_panel.hide()
	_tab.hide()
	_menu.hide()
	_more.hide()


func _open(who: String) -> void:
	_panel.show()
	_tab.visible = who != ""
	_tab_label.text = who
	_tab.size.x = who.length() * 5 + 12
	_text.add_theme_color_override("font_color", Color.WHITE if who != "" else NARRATION)
	_more.hide()


# --------------------------------------------------------------------------------------------
# input
# --------------------------------------------------------------------------------------------

func _unhandled_input(event: InputEvent) -> void:
	if _state == "" or _state == "caption":
		return
	var a := ""
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_UP, KEY_W: a = "up"
			KEY_DOWN, KEY_S: a = "down"
			KEY_Z, KEY_ENTER, KEY_KP_ENTER, KEY_SPACE: a = "ok"
			KEY_X, KEY_ESCAPE: a = "cancel"
	elif event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_LEFT and _state != "menu":
			a = "ok"
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			a = "cancel"
	if a == "":
		return
	get_viewport().set_input_as_handled()
	match _state:
		"typing":
			if a in ["ok", "cancel"]:
				_skip = true
		"wait":
			if a in ["ok", "cancel"]:
				sfx.play("ok")
				_done.emit(null)
		"menu":
			match a:
				"up": _move(-1)
				"down": _move(1)
				"ok": _pick(_cursor)
				"cancel":
					if _cancelable:
						sfx.play("back")
						_done.emit(null)


func _enabled(i: int) -> bool:
	return bool(_items[i].get("enabled", true))


func _move(dir: int) -> void:
	var n := _items.size()
	for step in n:
		_cursor = (_cursor + dir + n) % n
		if _enabled(_cursor):
			break
	sfx.play("move")
	_refresh_menu()


func _pick(i: int) -> void:
	if _state != "menu" or not _enabled(i):
		return
	sfx.play("ok")
	_done.emit(_items[i]["value"])


func _hover(i: int) -> void:
	if _state == "menu" and _enabled(i) and i != _cursor:
		_cursor = i
		_refresh_menu()


func _row_gui(event: InputEvent, i: int) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		_cursor = i
		_pick(i)


func _refresh_menu() -> void:
	for i in _rows.size():
		_rows[i].text = ("> " if i == _cursor else "  ") + String(_items[i]["label"])
		_rows[i].add_theme_color_override("font_color", Color.WHITE if _enabled(i) else Color("#6a6488"))


# --------------------------------------------------------------------------------------------
# windows (the battle's look)
# --------------------------------------------------------------------------------------------

func _window(pos: Vector2, sz: Vector2) -> Panel:
	var p := Panel.new()
	p.position = pos
	p.size = sz
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.05, 0.035, 0.12, 0.92)
	sb.border_color = Color("#d6d0ff")
	sb.set_border_width_all(1)
	sb.set_corner_radius_all(2)
	p.add_theme_stylebox_override("panel", sb)
	add_child(p)
	return p


func _label(parent: Node, pos: Vector2, sz: Vector2) -> Label:
	var l := Label.new()
	l.position = pos
	l.size = sz
	l.add_theme_font_size_override("font_size", 8)
	l.add_theme_constant_override("line_spacing", 1)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(l)
	return l
