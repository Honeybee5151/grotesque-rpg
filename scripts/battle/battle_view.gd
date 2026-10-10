extends Node2D
## What a battle shows and hears: backdrop, enemy sprites and their poses, the log, status and
## command windows, menus and input, popups, hit effects and sounds. No rules live here; the
## battle (scripts/battle/battle.gd) tells the view what happened.

const Data := preload("res://scripts/data.gd")
const Sprites := preload("res://scripts/sprite_factory.gd")
const Sfx := preload("res://scripts/battle/sfx.gd")
const Battler := preload("res://scripts/battle/battler.gd")
# Popups: chunky digits with the outline baked in (0-9 + - ! ? . / space), and a 2px taller set for
# big hits (crits, hits on a stunned enemy). Text is the theme's Grotesk.
const DIGITS := preload("res://art/fonts/grotesk_digits.fnt")
const BIG_DIGITS := preload("res://art/fonts/grotesk_crit.fnt")

const HOLD := 0.65          # seconds a finished line stays before the next one
const GROUND_Y := 122.0     # enemies stand on this line, bottom-centred (docs/art.md)
const GAP := 4.0            # between enemy canvases; a formation is centred on x=160
const BAR_W := 44.0
const PLAYER_POPUP := Vector2(272, 118)
const ENEMY_POPUP_Y := 50.0
# Menus hug the left edge and grow upward from just above the log window, as narrow as their
# text, so they stay clear of a pair of enemies (formations start at x=54 or further in).
const MENU_LEFT := 4.0
const MENU_BOTTOM := 120.0
# art/monsters/<sprite>/<pose>.png at 1x, all on the same canvas (up to 104x118) and standing on
# its bottom row. Missing poses fall back to normal. In a pack, the n-th member with that sprite
# takes <pose>_<n>.png when there is one (normal_2, normal_3...), so they aren't clones.
const POSES := ["normal", "telegraph", "stunned", "hurt"]

const SHADER := """
shader_type canvas_item;
uniform vec4 flash_color : source_color = vec4(1.0);
uniform float flash : hint_range(0.0, 1.0) = 0.0;
uniform float dissolve : hint_range(0.0, 1.0) = 0.0;
void fragment() {
	vec4 c = texture(TEXTURE, UV);
	float h = fract(sin(dot(floor(UV / TEXTURE_PIXEL_SIZE), vec2(12.9898, 78.233))) * 43758.5453);
	if (h < dissolve) { c.a = 0.0; }
	c.rgb = mix(c.rgb, flash_color.rgb, flash * c.a);
	COLOR = c;
}
"""

signal menu_done(value)

var transcript: Array[String] = []  # every line said this battle (read by tools/smoke_test.gd)
var menu_open := false
var menu_items: Array = []
var menu_cursor := 0
var menu_serial := 0  # counts menus opened; a submenu can open in the frame its parent closes

var _skip_req := false
var _cancel_req := false
var _log_lines: Array[String] = []
var _menu_cancelable := false
var _menu_rows: Array[Label] = []
var _on_cursor := Callable()
var _fx_rng := RandomNumberGenerator.new()  # screen shake etc., kept off the battle's RNG
var _shader: Shader
var _foes: Dictionary = {}  # Battler -> {sprite, mat, poses, x, pose}
var _blink: Tween

var log_label: Label
var cmd_panel: Panel
var name_label: Label
var hp_fill: ColorRect
var mp_fill: ColorRect
var hp_num: Label
var mp_num: Label
var state_label: Label
var flash_rect: ColorRect


func build(bg: String, hero: Battler, enemies: Array) -> void:
	_build_backdrop(bg)
	_shader = Shader.new()
	_shader.code = SHADER
	# Canvases side by side, GAP apart, the whole formation centred.
	var poses: Array = []
	var nth := {}
	var total := GAP * (enemies.size() - 1)
	for e in enemies:
		var art: String = e.data.get("sprite", e.id)
		nth[art] = nth.get(art, 0) + 1
		poses.append(_load_poses(art, nth[art]))
		total += poses.back()["normal"].get_width()
	var left := floorf(160.0 - total / 2.0)
	for i in enemies.size():
		var w: float = poses[i]["normal"].get_width()
		_add_enemy(enemies[i], poses[i], floorf(left + w / 2.0))
		left += w + GAP
	_build_ui(hero)


# ======================================================================================
# Enemies
# ======================================================================================

func set_pose(b: Battler, pose: String) -> void:
	var f: Dictionary = _foes[b]
	f["pose"] = pose
	_show(f, f["poses"].get(pose, f["poses"]["normal"]))


# big: a crit or a hit on a stunned enemy -- louder sound, taller yellow number.
func hit_enemy(b: Battler, dmg: int, big: bool) -> void:
	var f: Dictionary = _foes[b]
	var mat: ShaderMaterial = f["mat"]
	sfx("crit" if big else "hit")
	mat.set_shader_parameter("flash_color", Color.WHITE)
	mat.set_shader_parameter("flash", 1.0)
	create_tween().tween_property(mat, "shader_parameter/flash", 0.0, 0.12)
	shake_enemy(b)
	if f["poses"].has("hurt"):
		_show(f, f["poses"]["hurt"])
		create_tween().tween_callback(_reshow.bind(b)).set_delay(0.3)
	_popup(str(dmg), _enemy_popup_pos(b), Color("#ffe14a") if big else Color.WHITE, BIG_DIGITS if big else DIGITS)


func shake_enemy(b: Battler) -> void:
	var s: Sprite2D = _foes[b]["sprite"]
	var x: float = _foes[b]["x"]
	var tw := create_tween()
	for i in 5:
		var amp := (4.0 if i % 2 == 0 else -4.0) * (1.0 - i / 5.0)
		tw.tween_property(s, "position:x", x + amp, 0.04)
	tw.tween_property(s, "position:x", x, 0.04)


func flash_enemy(b: Battler, col: Color) -> void:
	var mat: ShaderMaterial = _foes[b]["mat"]
	mat.set_shader_parameter("flash_color", col)
	mat.set_shader_parameter("flash", 0.8)
	create_tween().tween_property(mat, "shader_parameter/flash", 0.0, 0.25)


func kill_enemy(b: Battler) -> void:
	var f: Dictionary = _foes[b]
	var s: Sprite2D = f["sprite"]
	sfx("die")
	var tw := create_tween().set_parallel(true)
	tw.tween_property(f["mat"], "shader_parameter/dissolve", 1.0, 1.1)
	tw.tween_property(s, "position:y", GROUND_Y + 8.0, 1.1)
	await tw.finished
	s.hide()


# Blinks the enemy a target menu is pointing at; null stops it.
func select_enemy(b: Variant) -> void:
	if _blink:
		_blink.kill()
		_blink = null
	for foe in _foes:
		_foes[foe]["mat"].set_shader_parameter("flash", 0.0)
	if not b is Battler:
		return
	var mat: ShaderMaterial = _foes[b]["mat"]
	mat.set_shader_parameter("flash_color", Color.WHITE)
	_blink = create_tween().set_loops()
	_blink.tween_property(mat, "shader_parameter/flash", 0.45, 0.25)
	_blink.tween_property(mat, "shader_parameter/flash", 0.0, 0.25)


func popup_enemy(b: Battler, text: String, col: Color) -> void:
	_popup(text, _enemy_popup_pos(b), col)


func _load_poses(art: String, nth: int) -> Dictionary:
	var poses := {}
	for pose in POSES:
		for path in ["res://art/monsters/%s/%s_%d.png" % [art, pose, nth], "res://art/monsters/%s/%s.png" % [art, pose]]:
			if ResourceLoader.exists(path):
				poses[pose] = load(path)
				break
	if not poses.has("normal"):
		push_warning("no art/monsters/%s/normal.png, drawing a placeholder" % art)
		var img := Image.create_empty(24, 24, false, Image.FORMAT_RGBA8)
		img.fill(Color("#ff00ff"))
		poses["normal"] = ImageTexture.create_from_image(img)
	return poses


func _add_enemy(b: Battler, poses: Dictionary, x: float) -> void:
	var mat := ShaderMaterial.new()
	mat.shader = _shader
	mat.set_shader_parameter("flash", 0.0)  # set up front: tweens need them to exist
	mat.set_shader_parameter("dissolve", 0.0)
	var s := Sprite2D.new()
	s.centered = false
	s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	s.material = mat
	s.position = Vector2(x, GROUND_Y)
	add_child(s)
	_foes[b] = {"sprite": s, "mat": mat, "poses": poses, "x": x, "pose": "normal"}
	set_pose(b, "normal")


# Bottom-centre anchor: every pose stands on the ground line whatever its canvas.
func _show(f: Dictionary, tex: Texture2D) -> void:
	var s: Sprite2D = f["sprite"]
	s.texture = tex
	s.offset = Vector2(-floorf(tex.get_width() / 2.0), -tex.get_height())


func _reshow(b: Battler) -> void:
	set_pose(b, _foes[b]["pose"])


func _enemy_popup_pos(b: Battler) -> Vector2:
	return Vector2(_foes[b]["x"], ENEMY_POPUP_Y)


# ======================================================================================
# Hero
# ======================================================================================

func hurt_hero(lost: int) -> void:
	sfx("hurt")
	flash_rect.color = Color(0.8, 0.0, 0.05, 0.45)
	create_tween().tween_property(flash_rect, "color:a", 0.0, 0.3)
	var tw := create_tween()
	for i in 6:
		tw.tween_property(self, "position", Vector2(_fx_rng.randf_range(-3, 3), _fx_rng.randf_range(-2, 2)), 0.04)
	tw.tween_property(self, "position", Vector2.ZERO, 0.04)
	_popup(str(lost), PLAYER_POPUP, Color("#ff6b6b"))


func popup_hero(text: String, col: Color) -> void:
	_popup(text, PLAYER_POPUP, col)


# The mute hero's speech bubble: a gesture, never words.
func hero_gestures(text: String) -> void:
	_popup(text, PLAYER_POPUP, Color("#b8b0e0"))


func refresh_status(h: Battler) -> void:
	hp_fill.size.x = BAR_W * float(h.hp) / h.max_hp
	hp_fill.color = Color("#ff5a5a") if h.hp * 10 < h.max_hp * 3 else Color("#59d36b")
	mp_fill.size.x = BAR_W * float(h.mp) / h.max_mp
	hp_num.text = str(h.hp)
	mp_num.text = str(h.mp)
	var labels: Array[String] = []
	for s in h.states:
		labels.append(String(Data.STATES[s].get("label", s.to_upper())).replace("{stacks}", str(h.states[s])))
	state_label.text = " ".join(labels)


# ======================================================================================
# Text, menus, input
# ======================================================================================

func say(text: String, hold: float = HOLD) -> void:
	if _text_width(log_label, text) > log_label.size.x:
		push_warning("too wide for the log window: " + text)
	transcript.append(text)
	_log_lines.append("")
	if _log_lines.size() > 3:
		_log_lines.pop_front()
	var idx := _log_lines.size() - 1
	_skip_req = false
	var n := 2
	while n < text.length() + 2 and not _skip_req:
		_log_lines[idx] = text.substr(0, n)
		_refresh_log()
		await get_tree().process_frame
		n += 2
	_log_lines[idx] = text
	_refresh_log()
	await _sleep(hold)


func _sleep(sec: float, skippable: bool = true) -> void:
	_skip_req = false
	var t := 0.0
	while t < sec:
		if skippable and _skip_req:
			break
		await get_tree().process_frame
		t += get_process_delta_time()
	_skip_req = false


# Returns true for confirm, false for cancel.
func wait_choice() -> bool:
	_skip_req = false
	_cancel_req = false
	while not _skip_req and not _cancel_req:
		await get_tree().process_frame
	var ok := _skip_req
	_skip_req = false
	_cancel_req = false
	return ok


# rows: [{label, value, enabled?}]. Returns the picked value, or null when cancelled.
# on_cursor(value) is called whenever the cursor lands on a row.
func menu(rows: Array, cancelable: bool = false, on_cursor: Callable = Callable()) -> Variant:
	for r in _menu_rows:
		r.queue_free()
	_menu_rows.clear()
	menu_items = rows
	_menu_cancelable = cancelable
	_on_cursor = on_cursor
	var widest := 0.0
	for it in rows:
		widest = maxf(widest, _text_width(cmd_panel, "> " + String(it["label"])))
	cmd_panel.size = Vector2(ceili(widest) + 12, 8 + rows.size() * 11)
	cmd_panel.position = Vector2(MENU_LEFT, MENU_BOTTOM - cmd_panel.size.y)
	for i in rows.size():
		var row := _make_label(cmd_panel, Vector2(5, 4 + i * 11), Vector2(cmd_panel.size.x - 8, 11))
		row.mouse_filter = Control.MOUSE_FILTER_STOP
		row.mouse_entered.connect(_on_row_hover.bind(i))
		row.gui_input.connect(_on_row_gui.bind(i))
		_menu_rows.append(row)
	menu_cursor = 0
	if not _row_enabled(0):
		_menu_move(1)
	_menu_refresh()
	cmd_panel.show()
	menu_open = true
	menu_serial += 1
	var result: Variant = await menu_done
	menu_open = false
	cmd_panel.hide()
	return result


func _row_enabled(i: int) -> bool:
	return bool(menu_items[i].get("enabled", true))


func _menu_move(dir: int) -> void:
	var n := menu_items.size()
	for step in n:
		menu_cursor = (menu_cursor + dir + n) % n
		if _row_enabled(menu_cursor):
			break
	_menu_refresh()


func _menu_refresh() -> void:
	for i in _menu_rows.size():
		var row := _menu_rows[i]
		row.text = ("> " if i == menu_cursor else "  ") + String(menu_items[i]["label"])
		row.add_theme_color_override("font_color", Color.WHITE if _row_enabled(i) else Color("#6a6488"))
	if _on_cursor.is_valid():
		_on_cursor.call(menu_items[menu_cursor]["value"])


func _menu_pick(i: int) -> void:
	if not menu_open or not _row_enabled(i):
		return
	sfx("ok")
	menu_done.emit(menu_items[i]["value"])


func _on_row_hover(i: int) -> void:
	if menu_open and _row_enabled(i):
		menu_cursor = i
		_menu_refresh()


func _on_row_gui(event: InputEvent, i: int) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		menu_cursor = i
		_menu_pick(i)


func _unhandled_input(event: InputEvent) -> void:
	var a := ""
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_UP, KEY_W: a = "up"
			KEY_DOWN, KEY_S: a = "down"
			KEY_Z, KEY_ENTER, KEY_KP_ENTER, KEY_SPACE: a = "ok"
			KEY_X, KEY_ESCAPE: a = "cancel"
			KEY_M: Sfx.muted = not Sfx.muted
	elif event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_LEFT and not menu_open:
			a = "ok"
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			a = "cancel"
	if a != "":
		action(a)


func action(a: String) -> void:
	if menu_open:
		match a:
			"up": _menu_move(-1)
			"down": _menu_move(1)
			"ok": _menu_pick(menu_cursor)
			"cancel":
				if _menu_cancelable:
					menu_done.emit(null)
	elif a == "ok":
		_skip_req = true
	elif a == "cancel":
		_cancel_req = true


func sfx(sound: String) -> void:
	Sfx.play(sound, self)


# ======================================================================================
# Scene building
# ======================================================================================

func _build_backdrop(bg: String) -> void:
	if bg != "cave":
		push_warning("unknown battle backdrop '%s', using the cave" % bg)
	var back := Sprite2D.new()
	back.texture = ImageTexture.create_from_image(Sprites.build_background())
	back.centered = false
	add_child(back)


func _make_window(pos: Vector2, sz: Vector2) -> Panel:
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


func _make_label(parent: Node, pos: Vector2, sz: Vector2) -> Label:
	var l := Label.new()
	l.position = pos
	l.size = sz
	l.add_theme_constant_override("line_spacing", 1)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(l)
	return l


func _make_bar(parent: Node, pos: Vector2, col: Color) -> ColorRect:
	var back := ColorRect.new()
	back.position = pos
	back.size = Vector2(BAR_W, 5)
	back.color = Color("#2a2342")
	back.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(back)
	var fill := ColorRect.new()
	fill.position = pos
	fill.size = Vector2(BAR_W, 5)
	fill.color = col
	fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(fill)
	return fill


func _build_ui(hero: Battler) -> void:
	var log_panel := _make_window(Vector2(0, 124), Vector2(224, 56))
	log_label = _make_label(log_panel, Vector2(5, 3), Vector2(214, 50))

	var st := _make_window(Vector2(224, 124), Vector2(96, 56))
	name_label = _make_label(st, Vector2(5, 2), Vector2(86, 11))
	name_label.text = hero.name
	_make_label(st, Vector2(5, 15), Vector2(14, 11)).text = "HP"
	hp_fill = _make_bar(st, Vector2(19, 18), Color("#59d36b"))
	hp_num = _make_label(st, Vector2(66, 15), Vector2(25, 11))
	hp_num.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_make_label(st, Vector2(5, 27), Vector2(14, 11)).text = "MP"
	mp_fill = _make_bar(st, Vector2(19, 30), Color("#5a9bff"))
	mp_num = _make_label(st, Vector2(66, 27), Vector2(25, 11))
	mp_num.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	state_label = _make_label(st, Vector2(5, 41), Vector2(86, 11))
	state_label.add_theme_color_override("font_color", Color("#ff6b8b"))

	cmd_panel = _make_window(Vector2(6, 64), Vector2(70, 52))
	cmd_panel.hide()

	flash_rect = ColorRect.new()
	flash_rect.size = Vector2(320, 180)
	flash_rect.color = Color(0, 0, 0, 0)
	flash_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(flash_rect)
	refresh_status(hero)


func _refresh_log() -> void:
	log_label.text = "\n".join(_log_lines)


# Pixel width of a line in the theme font, as a Label under `node` would draw it.
func _text_width(node: Control, text: String) -> float:
	var font := node.get_theme_font("font", "Label")
	return font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, node.get_theme_font_size("font_size", "Label")).x


# ======================================================================================
# Effects
# ======================================================================================

func _popup(text: String, pos: Vector2, col: Color, font: Font = DIGITS) -> void:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", font)
	l.add_theme_color_override("font_color", col)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.size = Vector2(40, 14)
	l.position = pos - Vector2(20, 8)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(l)
	var tw := create_tween().set_parallel(true)
	tw.tween_property(l, "position:y", l.position.y - 14.0, 0.8)
	tw.tween_property(l, "modulate:a", 0.0, 0.35).set_delay(0.45)
	tw.chain().tween_callback(l.queue_free)
