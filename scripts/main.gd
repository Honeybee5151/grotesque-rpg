extends Node2D
## Tutorial battle: Wanderer vs the Host (a possessed man with the Sucker Frog on his shoulders).
## Classic turn-based combat, written as plain GDScript coroutines (no battle framework).
## Flow: _run_game -> _battle -> (command phase -> hero acts -> enemy acts -> end of turn)*

const Data := preload("res://scripts/data.gd")
const Sprites := preload("res://scripts/sprite_factory.gd")

const ENEMY_REST_Y := 63.0
const BAR_W := 44.0
const PLAYER_POPUP := Vector2(272, 118)
const ENEMY_POPUP := Vector2(160, 50)

const SHADER := """
shader_type canvas_item;
uniform vec4 flash_color : source_color = vec4(1.0);
uniform float flash : hint_range(0.0, 1.0) = 0.0;
uniform float dissolve : hint_range(0.0, 1.0) = 0.0;
void fragment() {
	vec4 c = texture(TEXTURE, UV);
	float h = fract(sin(dot(floor(UV * 56.0), vec2(12.9898, 78.233))) * 43758.5453);
	if (h < dissolve) { c.a = 0.0; }
	c.rgb = mix(c.rgb, flash_color.rgb, flash * c.a);
	COLOR = c;
}
"""

signal menu_done(value)

# --- hero state ---
var hn: String
var hp: int
var mp: int
var guarding := false
var drained := 0
var items: Dictionary = {}

# --- enemy state ---
var e_data: Dictionary
var e_hp: int
var e_idx := 0
var e_stunned := false

# --- UI / flow state ---
var muted := false
var _skip_req := false
var _cancel_req := false
var _log_lines: Array[String] = []
var transcript: Array[String] = []  # every line said this battle (read by tools/smoke_test.gd)
var _fx_rng := RandomNumberGenerator.new()  # screen shake etc., kept off the battle's RNG
var _menu_open := false
var _menu_items: Array = []
var _menu_cursor := 0
var _menu_cancelable := false
var _menu_rows: Array[Label] = []
var _sfx: Dictionary = {}

# --- nodes ---
var enemy_sprite: Sprite2D
var enemy_mat: ShaderMaterial
var tex_frog: ImageTexture
var tex_coiled: ImageTexture
var log_label: Label
var cmd_panel: Panel
var name_label: Label
var hp_fill: ColorRect
var mp_fill: ColorRect
var hp_num: Label
var mp_num: Label
var state_label: Label
var flash_rect: ColorRect


func _ready() -> void:
	RenderingServer.set_default_clear_color(Color("#07050d"))
	_build_world()
	_build_ui()
	_build_audio()
	_run_game()


# ======================================================================================
# Game flow
# ======================================================================================

func _run_game() -> void:
	while true:
		await _battle()
		await say("Z: fight again    X: title screen", 0.0)
		if not await _wait_choice():
			get_tree().change_scene_to_file("res://title.tscn")
			return


func _battle() -> void:
	_reset_battle("sucker_frog")
	_log_lines.clear()
	transcript.clear()
	_refresh_log()
	await say("A man staggers out of the dark.")
	await say("Something wet rides his shoulders.")
	_popup("...", PLAYER_POPUP, Color("#b8b0e0"), 10)
	await say("%s says nothing. He nods, once." % hn)

	while true:
		guarding = false
		var act: Dictionary = await _command_phase()
		# The hero (agi 10) always outpaces the frog (agi 6) so order is fixed for now.
		# When you add faster enemies, sort the actors by agi here.
		await _hero_act(act)
		if e_hp <= 0:
			break
		await _enemy_act()
		if hp <= 0:
			break
		await _end_of_turn()
		if hp <= 0:
			break

	if e_hp <= 0:
		await _victory()
	else:
		await _defeat()


func _command_phase() -> Dictionary:
	while true:
		var cmd: Variant = await _menu([
			{"label": "Attack", "value": "attack"},
			{"label": "Guard", "value": "guard"},
			{"label": "Item", "value": "item"},
			{"label": "Run", "value": "run", "enabled": false},
		])
		if cmd == "item":
			var id: Variant = await _item_menu()
			if id == null:
				continue
			return {"type": "item", "id": id}
		return {"type": cmd}
	return {}


func _item_menu() -> Variant:
	var rows: Array = []
	for id in Data.ITEMS:
		var it: Dictionary = Data.ITEMS[id]
		var have: int = items.get(id, 0)
		rows.append({
			"label": "%s x%d" % [it["name"], have],
			"value": id,
			"enabled": have > 0 and _item_usable(it),
		})
	return await _menu(rows, true)


func _item_usable(it: Dictionary) -> bool:
	return hp < int(Data.HERO["max_hp"]) or (drained > 0 and bool(it["cures_drained"]))


# --------------------------------------------------------------------------------------
# Hero
# --------------------------------------------------------------------------------------

func _hero_act(a: Dictionary) -> void:
	match a["type"]:
		"attack":
			# Drained saps 10% attack per stack.
			var d := roundi(float(Data.HERO["atk"]) * (1.0 - 0.1 * drained) * randf_range(0.85, 1.15)) - int(e_data["def"])
			var crit := randf() < 0.1
			if crit:
				d = roundi(d * 1.5)
			d = maxi(1, d)
			e_hp = maxi(0, e_hp - d)
			sfx("crit" if crit else "hit")
			_hit_enemy()
			_popup(str(d), ENEMY_POPUP, Color("#ffe14a") if crit else Color.WHITE, 14 if crit else 12)
			if crit:
				await say("A clean hit! The Host takes %d." % d)
			else:
				await say("%s strikes! The Host takes %d." % [hn, d])
		"guard":
			guarding = true
			sfx("guard")
			await say("%s braces himself." % hn)
		"item":
			var id: String = a["id"]
			var it: Dictionary = Data.ITEMS[id]
			items[id] = int(items[id]) - 1
			var healed := mini(int(it["heal"]), int(Data.HERO["max_hp"]) - hp)
			var cured := drained > 0 and bool(it["cures_drained"])
			hp += healed
			if cured:
				drained = 0
			sfx("heal")
			_refresh_status()
			if healed > 0:
				_popup("+%d" % healed, PLAYER_POPUP, Color("#7dff8c"))
			await say("%s smears on a Salve." % hn)
			await say("%d HP restored.%s" % [healed, " The drain lifts." if cured else ""])


# --------------------------------------------------------------------------------------
# Enemy: lash -> coil (telegraph) -> latch
# --------------------------------------------------------------------------------------

func _enemy_act() -> void:
	if e_stunned:
		e_stunned = false
		e_idx = 0
		await say("The Host is still reeling.")
		return
	var pattern: Array = e_data["pattern"]
	var skill: String = pattern[e_idx % pattern.size()]
	e_idx += 1
	match skill:
		"lash": await _skill_lash()
		"coil": await _skill_coil()
		"latch": await _skill_latch()


func _skill_lash() -> void:
	await say("A tongue lashes out of the Host's mouth!")
	var d := randi_range(5, 8)
	if guarding:
		d = ceili(d / 2.0)
	var lost := _hurt_hero(d)
	await say("%s takes %d damage.%s" % [hn, lost, " (guarded)" if guarding else ""])


func _skill_coil() -> void:
	await say("The Host's head tips back, jaw unhinged.", 0.35)
	enemy_sprite.texture = tex_coiled
	enemy_mat.set_shader_parameter("flash_color", Color("#ffb0c8"))
	enemy_mat.set_shader_parameter("flash", 0.8)
	create_tween().tween_property(enemy_mat, "shader_parameter/flash", 0.0, 0.25)
	sfx("coil")
	await say("The sucker flexes on its brain, hungry.")


func _skill_latch() -> void:
	await say("The sucker lunges for %s's head!" % hn, 0.5)
	if guarding:
		sfx("guard")
		_shake_enemy()
		await say("It slaps his raised arms and slips off!")
		e_stunned = true
		await say("The Host reels, stunned.")
	else:
		var lost := _hurt_hero(randi_range(4, 6))
		drained = mini(3, drained + 1)
		sfx("drain")
		_refresh_status()
		await say("It clamps on! He takes %d damage." % lost)
		await say("Drained x%d! Something warm slips away." % drained)
	enemy_sprite.texture = tex_frog


func _hurt_hero(d: int) -> int:
	var before := hp
	hp = maxi(1 if Data.MERCY else 0, hp - d)
	var lost := before - hp
	sfx("hurt")
	_hurt_fx()
	_popup(str(lost), PLAYER_POPUP, Color("#ff6b6b"))
	_refresh_status()
	return lost


# Drained ticks every turn: 3 HP and 1 MP per stack. Cure it with a Salve or kill the frog.
func _end_of_turn() -> void:
	if drained <= 0:
		return
	var before := hp
	hp = maxi(1 if Data.MERCY else 0, hp - drained * 3)
	var lost := before - hp
	var mp_loss := mini(mp, drained)
	mp -= mp_loss
	sfx("drain")
	_popup("-%d" % lost, PLAYER_POPUP, Color("#ff9ab8"), 10)
	_refresh_status()
	await say("Drained... -%d HP, -%d MP." % [lost, mp_loss], 0.5)


func _victory() -> void:
	drained = 0
	_refresh_status()
	sfx("die")
	var tw := create_tween().set_parallel(true)
	tw.tween_property(enemy_mat, "shader_parameter/dissolve", 1.0, 1.1)
	tw.tween_property(enemy_sprite, "position:y", ENEMY_REST_Y + 8.0, 1.1)
	await tw.finished
	enemy_sprite.hide()
	await say("The frog peels away, spent. The man falls.")
	await say("He was already gone.")
	await say("Victory.")


func _defeat() -> void:
	await say("%s collapses." % hn)
	await say("Everything goes quiet.")


func _reset_battle(enemy_id: String) -> void:
	hn = Data.HERO["name"]
	hp = Data.HERO["max_hp"]
	mp = Data.HERO["max_mp"]
	guarding = false
	drained = 0
	items = {}
	for id in Data.ITEMS:
		items[id] = Data.ITEMS[id]["start"]
	e_data = Data.ENEMIES[enemy_id]
	e_hp = e_data["max_hp"]
	e_idx = 0
	e_stunned = false
	enemy_sprite.show()
	enemy_sprite.texture = tex_frog
	enemy_sprite.position = Vector2(160, ENEMY_REST_Y)
	enemy_mat.set_shader_parameter("dissolve", 0.0)
	enemy_mat.set_shader_parameter("flash", 0.0)
	_refresh_status()


# ======================================================================================
# Text, menus, input
# ======================================================================================

func say(text: String, hold: float = 0.65) -> void:
	if text.length() > 44:
		push_warning("message too long for the log window: " + text)
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
func _wait_choice() -> bool:
	_skip_req = false
	_cancel_req = false
	while not _skip_req and not _cancel_req:
		await get_tree().process_frame
	var ok := _skip_req
	_skip_req = false
	_cancel_req = false
	return ok


func _menu(items_in: Array, cancelable: bool = false) -> Variant:
	for r in _menu_rows:
		r.queue_free()
	_menu_rows.clear()
	_menu_items = items_in
	_menu_cancelable = cancelable
	var widest := 0
	for it in items_in:
		widest = maxi(widest, String(it["label"]).length())
	cmd_panel.size = Vector2(maxi(70, widest * 5 + 18), 8 + items_in.size() * 11)
	for i in items_in.size():
		var row := _make_label(cmd_panel, Vector2(5, 4 + i * 11), Vector2(cmd_panel.size.x - 8, 11))
		row.mouse_filter = Control.MOUSE_FILTER_STOP
		row.mouse_entered.connect(_on_row_hover.bind(i))
		row.gui_input.connect(_on_row_gui.bind(i))
		_menu_rows.append(row)
	_menu_cursor = 0
	if not _row_enabled(0):
		_menu_move(1)
	_menu_refresh()
	cmd_panel.show()
	_menu_open = true
	var result: Variant = await menu_done
	_menu_open = false
	cmd_panel.hide()
	return result


func _row_enabled(i: int) -> bool:
	return bool(_menu_items[i].get("enabled", true))


func _menu_move(dir: int) -> void:
	var n := _menu_items.size()
	for step in n:
		_menu_cursor = (_menu_cursor + dir + n) % n
		if _row_enabled(_menu_cursor):
			break
	_menu_refresh()


func _menu_refresh() -> void:
	for i in _menu_rows.size():
		var row := _menu_rows[i]
		row.text = ("> " if i == _menu_cursor else "  ") + String(_menu_items[i]["label"])
		row.add_theme_color_override("font_color", Color.WHITE if _row_enabled(i) else Color("#6a6488"))


func _menu_pick(i: int) -> void:
	if not _menu_open or not _row_enabled(i):
		return
	sfx("ok")
	menu_done.emit(_menu_items[i]["value"])


func _on_row_hover(i: int) -> void:
	if _menu_open and _row_enabled(i):
		_menu_cursor = i
		_menu_refresh()


func _on_row_gui(event: InputEvent, i: int) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		_menu_cursor = i
		_menu_pick(i)


func _unhandled_input(event: InputEvent) -> void:
	var a := ""
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_UP, KEY_W: a = "up"
			KEY_DOWN, KEY_S: a = "down"
			KEY_Z, KEY_ENTER, KEY_KP_ENTER, KEY_SPACE: a = "ok"
			KEY_X, KEY_ESCAPE: a = "cancel"
			KEY_M: muted = not muted
	elif event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_LEFT and not _menu_open:
			a = "ok"
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			a = "cancel"
	if a != "":
		_action(a)


func _action(a: String) -> void:
	if _menu_open:
		match a:
			"up": _menu_move(-1)
			"down": _menu_move(1)
			"ok": _menu_pick(_menu_cursor)
			"cancel":
				if _menu_cancelable:
					menu_done.emit(null)
	elif a == "ok":
		_skip_req = true
	elif a == "cancel":
		_cancel_req = true


# ======================================================================================
# Scene building
# ======================================================================================

func _build_world() -> void:
	var bg := Sprite2D.new()
	bg.texture = ImageTexture.create_from_image(Sprites.build_background())
	bg.centered = false
	add_child(bg)

	tex_frog = ImageTexture.create_from_image(Sprites.build_host(false))
	tex_coiled = ImageTexture.create_from_image(Sprites.build_host(true))
	var sh := Shader.new()
	sh.code = SHADER
	enemy_mat = ShaderMaterial.new()
	enemy_mat.shader = sh
	enemy_sprite = Sprite2D.new()
	enemy_sprite.texture = tex_frog
	enemy_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	enemy_sprite.scale = Vector2(2, 2)
	enemy_sprite.position = Vector2(160, ENEMY_REST_Y)
	enemy_sprite.material = enemy_mat
	add_child(enemy_sprite)


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


func _make_label(parent: Node, pos: Vector2, sz: Vector2, font_size: int = 8) -> Label:
	var l := Label.new()
	l.position = pos
	l.size = sz
	l.add_theme_font_size_override("font_size", font_size)
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


func _build_ui() -> void:
	var log_panel := _make_window(Vector2(0, 124), Vector2(224, 56))
	log_label = _make_label(log_panel, Vector2(5, 3), Vector2(214, 50))

	var st := _make_window(Vector2(224, 124), Vector2(96, 56))
	name_label = _make_label(st, Vector2(5, 2), Vector2(86, 11))
	name_label.text = Data.HERO["name"]
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


func _refresh_log() -> void:
	log_label.text = "\n".join(_log_lines)


func _refresh_status() -> void:
	var mh: int = Data.HERO["max_hp"]
	var mm: int = Data.HERO["max_mp"]
	hp_fill.size.x = BAR_W * float(hp) / mh
	hp_fill.color = Color("#ff5a5a") if hp * 10 < mh * 3 else Color("#59d36b")
	mp_fill.size.x = BAR_W * float(mp) / mm
	hp_num.text = str(hp)
	mp_num.text = str(mp)
	state_label.text = ("DRAINED x%d" % drained) if drained > 0 else ""


# ======================================================================================
# Effects
# ======================================================================================

func _hit_enemy() -> void:
	enemy_mat.set_shader_parameter("flash_color", Color.WHITE)
	enemy_mat.set_shader_parameter("flash", 1.0)
	create_tween().tween_property(enemy_mat, "shader_parameter/flash", 0.0, 0.12)
	_shake_enemy()


func _shake_enemy() -> void:
	var tw := create_tween()
	for i in 5:
		var amp := (4.0 if i % 2 == 0 else -4.0) * (1.0 - i / 5.0)
		tw.tween_property(enemy_sprite, "position:x", 160.0 + amp, 0.04)
	tw.tween_property(enemy_sprite, "position:x", 160.0, 0.04)


func _hurt_fx() -> void:
	flash_rect.color = Color(0.8, 0.0, 0.05, 0.45)
	create_tween().tween_property(flash_rect, "color:a", 0.0, 0.3)
	var tw := create_tween()
	for i in 6:
		tw.tween_property(self, "position", Vector2(_fx_rng.randf_range(-3, 3), _fx_rng.randf_range(-2, 2)), 0.04)
	tw.tween_property(self, "position", Vector2.ZERO, 0.04)


func _popup(text: String, pos: Vector2, col: Color, font_size: int = 12) -> void:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", col)
	l.add_theme_color_override("font_outline_color", Color.BLACK)
	l.add_theme_constant_override("outline_size", 3)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.size = Vector2(40, 14)
	l.position = pos - Vector2(20, 8)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(l)
	var tw := create_tween().set_parallel(true)
	tw.tween_property(l, "position:y", l.position.y - 14.0, 0.8)
	tw.tween_property(l, "modulate:a", 0.0, 0.35).set_delay(0.45)
	tw.chain().tween_callback(l.queue_free)


# ======================================================================================
# Audio: tiny synthesized beeps, no sound files. Press M to mute.
# ======================================================================================

func _build_audio() -> void:
	_sfx["ok"] = _synth([{"f0": 500, "f1": 500, "dur": 0.04, "k": "square", "v": 0.12}])
	_sfx["hit"] = _synth([{"f0": 220, "f1": 60, "dur": 0.12, "k": "square", "v": 0.3}])
	_sfx["crit"] = _synth([
		{"f0": 330, "f1": 80, "dur": 0.14, "k": "square", "v": 0.3},
		{"f0": 660, "f1": 120, "dur": 0.10, "k": "square", "v": 0.2, "delay": 0.05},
	])
	_sfx["hurt"] = _synth([{"f0": 140, "f1": 40, "dur": 0.22, "k": "saw", "v": 0.3}])
	_sfx["guard"] = _synth([{"f0": 300, "f1": 500, "dur": 0.08, "k": "tri", "v": 0.35}])
	_sfx["coil"] = _synth([{"f0": 90, "f1": 160, "dur": 0.35, "k": "saw", "v": 0.22}])
	_sfx["drain"] = _synth([
		{"f0": 400, "f1": 100, "dur": 0.4, "k": "sine", "v": 0.35},
		{"f0": 300, "f1": 70, "dur": 0.4, "k": "sine", "v": 0.25, "delay": 0.1},
	])
	_sfx["heal"] = _synth([
		{"f0": 440, "f1": 440, "dur": 0.08, "k": "tri", "v": 0.3},
		{"f0": 660, "f1": 660, "dur": 0.12, "k": "tri", "v": 0.3, "delay": 0.09},
	])
	_sfx["die"] = _synth([{"f0": 160, "f1": 30, "dur": 1.0, "k": "saw", "v": 0.3}])


func _synth(parts: Array) -> AudioStreamWAV:
	var rate := 22050
	var total := 0.0
	for p in parts:
		total = maxf(total, float(p.get("delay", 0.0)) + float(p["dur"]))
	var n := int(total * rate)
	var buf := PackedFloat32Array()
	buf.resize(n)
	for p in parts:
		var f0: float = p["f0"]
		var f1: float = p["f1"]
		var dur: float = p["dur"]
		var kind: String = p["k"]
		var vol: float = p.get("v", 0.25)
		var start := int(float(p.get("delay", 0.0)) * rate)
		var phase := 0.0
		for i in int(dur * rate):
			var t := float(i) / rate
			phase += f0 * pow(f1 / f0, t / dur) / rate
			var ph := fmod(phase, 1.0)
			var w := 0.0
			match kind:
				"sine": w = sin(TAU * ph)
				"square": w = 1.0 if ph < 0.5 else -1.0
				"saw": w = 2.0 * ph - 1.0
				"tri": w = 4.0 * absf(ph - 0.5) - 1.0
			buf[start + i] += w * vol * exp(-5.0 * t / dur)
	var bytes := PackedByteArray()
	bytes.resize(n * 2)
	for i in n:
		bytes.encode_s16(i * 2, int(clampf(buf[i], -1.0, 1.0) * 32767.0))
	var s := AudioStreamWAV.new()
	s.format = AudioStreamWAV.FORMAT_16_BITS
	s.mix_rate = rate
	s.stereo = false
	s.data = bytes
	return s


func sfx(sound: String) -> void:
	if muted or not _sfx.has(sound):
		return
	var pl := AudioStreamPlayer.new()
	pl.stream = _sfx[sound]
	pl.finished.connect(pl.queue_free)
	add_child(pl)
	pl.play()
