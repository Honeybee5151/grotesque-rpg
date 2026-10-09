extends RefCounted
## Procedural pixel art. Everything is drawn from code, so the project ships with no art files.
## Replace these with hand-made PNGs whenever you like.

const GW := 56
const GH := 56
const BAYER := [[0, 2], [3, 1]]


static func _put(img: Image, x: int, y: int, c: Color) -> void:
	if x >= 0 and y >= 0 and x < img.get_width() and y < img.get_height():
		img.set_pixel(x, y, c)


static func _solid(img: Image, x: int, y: int) -> bool:
	if x < 0 or y < 0 or x >= img.get_width() or y >= img.get_height():
		return false
	return img.get_pixel(x, y).a > 0.0


## Filled ellipse, shaded from a 4-colour ramp (dark..light) with light from the top-left,
## ordered-dithered so the shading bands look like hand-placed pixels.
static func _ell(img: Image, cx: float, cy: float, rx: float, ry: float, ramp: Array[Color]) -> void:
	for y in range(int(floor(cy - ry)), int(ceil(cy + ry)) + 1):
		for x in range(int(floor(cx - rx)), int(ceil(cx + rx)) + 1):
			var nx := (x - cx) / rx
			var ny := (y - cy) / ry
			if nx * nx + ny * ny > 1.0:
				continue
			var b: int = BAYER[y & 1][x & 1]
			var l := -(nx * 0.5 + ny * 0.7) + (b - 1.5) * 0.09
			var i := 3 if l > 0.55 else (2 if l > 0.1 else (1 if l > -0.45 else 0))
			_put(img, x, y, ramp[i])


static func _grin_y(x: int, base: int) -> int:
	return base + roundi(3.0 * (1.0 - pow((x - 28) / 15.0, 2.0)))


static func _eye(img: Image, cx: int, cy: int, sclera: Array[Color], skin: Array[Color], coiled: bool) -> void:
	_ell(img, cx, cy, 4, 4, sclera)
	var vein := Color("#4a0808") if coiled else Color("#a01818")
	var offs: Array[Vector2i] = [Vector2i(-3, 0), Vector2i(-2, -2), Vector2i(3, 1), Vector2i(2, 2), Vector2i(-2, 2), Vector2i(3, -1)]
	for o in offs:
		_put(img, cx + o.x, cy + o.y, vein)
	for y in range(cy - 3, cy + 4):
		_put(img, cx, y, Color.BLACK)
	for y in range(cy - 2, cy + 3):
		_put(img, cx + 1, y, Color.BLACK)
	if not coiled:
		# heavy lids: it's bored of you
		for x in range(cx - 4, cx + 5):
			for y in [cy - 4, cy - 3]:
				if _solid(img, x, y):
					_put(img, x, y, skin[1])


## The Sucker Frog. `coiled` is the telegraph pose: bigger sucker, wide red eyes.
static func build_frog(coiled: bool) -> Image:
	var rng := RandomNumberGenerator.new()
	rng.seed = 11
	var img := Image.create_empty(GW, GH, false, Image.FORMAT_RGBA8)

	var skin: Array[Color] = [Color("#243824"), Color("#37633a"), Color("#5f9440"), Color("#9cc04e")]
	var belly: Array[Color] = [Color("#6e5f40"), Color("#9b8a5e"), Color("#c4b27f"), Color("#e6d8a4")]
	var lip: Array[Color] = [Color("#4a0e2a"), Color("#8f1d4a"), Color("#c23366"), Color("#ef6f90")]
	var sclera: Array[Color] = [Color("#b08a22"), Color("#d8b83a"), Color("#ecd85c"), Color("#fff3a0")]
	if coiled:
		sclera = [Color("#8a1a1a"), Color("#c23030"), Color("#e85a5a"), Color("#ff9a9a")]
	var maw: Array[Color] = [Color("#1a0510"), Color("#2a0818"), Color("#3a0a1e"), Color("#4a0e2a")]
	var black: Array[Color] = [Color.BLACK, Color.BLACK, Color.BLACK, Color.BLACK]

	# legs, feet, body, head, belly, eye bulges
	_ell(img, 9, 44, 8, 6, skin)
	_ell(img, 46, 44, 8, 6, skin)
	_ell(img, 7, 51, 5, 3, skin)
	_ell(img, 49, 51, 5, 3, skin)
	_ell(img, 28, 35, 20, 15, skin)
	_ell(img, 28, 22, 15, 10, skin)
	_ell(img, 28, 42, 12, 7, belly)
	_ell(img, 15, 12, 6, 6, skin)
	_ell(img, 41, 12, 6, 6, skin)

	var r := 10 if coiled else 8
	var ri := 7 if coiled else 5
	var sx := 28
	var sy := 27

	# warts (always consume the same rng calls so both poses match)
	for n in 26:
		var x := rng.randi_range(0, GW - 1)
		var y := rng.randi_range(0, GH - 1)
		var c := img.get_pixel(x, y)
		if c.a > 0.0 and c.g > c.r and c.g > c.b and y > 10 and Vector2(x - sx, y - sy).length() > r + 2:
			_put(img, x, y, skin[0])
			_put(img, x - 1, y - 1, skin[3])
	# belly freckles
	for n in 14:
		var x := rng.randi_range(0, GW - 1)
		var y := rng.randi_range(0, GH - 1)
		var c := img.get_pixel(x, y)
		if c.a > 0.0 and c.r > c.g and y > 33:
			_put(img, x, y, belly[0])

	_eye(img, 15, 12, sclera, skin, coiled)
	_eye(img, 41, 12, sclera, skin, coiled)

	# the sucker: lipped disc, dark maw, black throat, two rings of teeth
	_ell(img, sx, sy, r, r, lip)
	_ell(img, sx, sy, ri, ri, maw)
	_ell(img, sx, sy, 2, 2, black)
	for a in 14:
		var t := a / 14.0 * TAU
		_put(img, roundi(sx + cos(t) * (ri - 0.5)), roundi(sy + sin(t) * (ri - 0.5)), Color("#f2ecd0"))
	for a in 9:
		var t := a / 9.0 * TAU
		_put(img, roundi(sx + cos(t) * (ri - 2.5)), roundi(sy + sin(t) * (ri - 2.5)), Color("#d8d0b0"))

	# the other mouth: wide grin under the sucker, mismatched teeth
	var gbase := 40 if coiled else 38
	for x in range(14, 43):
		var y := _grin_y(x, gbase)
		for k in 3:
			_put(img, x, y + k, Color("#14080c"))
	for x in range(15, 42, 2):
		var y := _grin_y(x, gbase)
		var n := 2 + int(rng.randf() * 2.0)
		for k in n:
			_put(img, x, y + k, Color("#ece5c4"))

	# drool
	var drool_len := 8 if coiled else 5
	for dx in [19, 33]:
		var y0 := _grin_y(dx, gbase) + 3
		for k in drool_len:
			_put(img, dx, y0 + k, Color("#8fd6e8"))
		_put(img, dx, y0 + drool_len, Color("#e0f8ff"))

	# 1px outline
	var out := Image.create_empty(GW, GH, false, Image.FORMAT_RGBA8)
	out.copy_from(img)
	var dirs: Array[Vector2i] = [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]
	for y in GH:
		for x in GW:
			if _solid(img, x, y):
				continue
			for d in dirs:
				if _solid(img, x + d.x, y + d.y):
					out.set_pixel(x, y, Color("#0d100c"))
					break
	return out


## 320x180 cave backdrop with a dithered glow behind the enemy and a floor shadow.
static func build_background() -> Image:
	var img := Image.create_empty(320, 180, false, Image.FORMAT_RGBA8)
	var rng := RandomNumberGenerator.new()
	rng.seed = 3
	var bands: Array[Color] = [Color("#0e0a18"), Color("#130e20"), Color("#18122a"), Color("#1d1631")]
	for y in 180:
		img.fill_rect(Rect2i(0, y, 320, 1), bands[mini(3, int(y / 32.0))])

	# dithered glow behind the enemy
	var glow := Color("#241a38")
	for y in range(8, 118):
		for x in range(90, 231):
			var nx := (x - 160) / 70.0
			var ny := (y - 62) / 52.0
			if nx * nx + ny * ny < 1.0 and (x + y) % 2 == 0:
				img.set_pixel(x, y, glow)

	# floor
	img.fill_rect(Rect2i(0, 96, 320, 84), Color("#241a2e"))
	for x in range(0, 320, 2):
		img.set_pixel(x, 95, Color("#241a2e"))
	for n in 90:
		img.set_pixel(rng.randi_range(0, 319), rng.randi_range(97, 123), Color("#2f2340"))

	# stalactites
	for n in 14:
		var x := rng.randi_range(0, 319)
		var h := rng.randi_range(6, 28)
		for yy in h:
			var half := roundi((1.0 - yy / float(h)) * 2.5)
			img.fill_rect(Rect2i(x - half, yy, half * 2 + 1, 1), Color("#0a0712"))

	# floor shadow
	for y in range(112, 123):
		for x in range(112, 209):
			var nx := (x - 160) / 46.0
			var ny := (y - 117) / 5.0
			if nx * nx + ny * ny <= 1.0:
				img.set_pixel(x, y, Color("#120c1a"))
	return img
