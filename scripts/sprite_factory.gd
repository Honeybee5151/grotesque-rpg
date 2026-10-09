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

	# dithered vignette: the edges of the cave swallow the light
	for y in 180:
		for x in 320:
			var nx := (x - 160.0) / 190.0
			var ny := (y - 80.0) / 105.0
			var v := nx * nx + ny * ny
			if v > 0.5:
				var t := clampf((v - 0.5) / 0.7, 0.0, 1.0)
				if t > float(BAYER[y & 1][x & 1]) / 4.0:
					img.set_pixel(x, y, img.get_pixel(x, y).darkened(0.55))
	return img


# ======================================================================================
# The Host: a possessed man with the Sucker Frog on his shoulders. The frog's sucker is seated
# in the open top of his skull and its cords run down into his brain and eyes.
# ======================================================================================

const HW := 52
const HH := 58


static func _line(img: Image, a: Vector2, b: Vector2, c: Color, w: int = 1) -> void:
	var n := int(maxf(absf(b.x - a.x), absf(b.y - a.y)))
	for i in n + 1:
		var t := float(i) / float(maxi(n, 1))
		var p := a.lerp(b, t)
		for dx in w:
			for dy in w:
				_put(img, int(p.x) + dx, int(p.y) + dy, c)


static func _outline(img: Image, col: Color) -> Image:
	var out := Image.create_empty(img.get_width(), img.get_height(), false, Image.FORMAT_RGBA8)
	out.copy_from(img)
	var dirs: Array[Vector2i] = [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]
	for y in img.get_height():
		for x in img.get_width():
			if _solid(img, x, y):
				continue
			for d in dirs:
				if _solid(img, x + d.x, y + d.y):
					out.set_pixel(x, y, col)
					break
	return out


static func _cord(img: Image, pts: Array[Vector2], dark: Color, hi: Color, w: int) -> void:
	for i in pts.size() - 1:
		_line(img, pts[i], pts[i + 1], dark, w)
	for i in pts.size():
		if i % 2 == 1:
			_put(img, int(pts[i].x), int(pts[i].y), hi)


static func build_host(coiled: bool) -> Image:
	var rng := RandomNumberGenerator.new()
	rng.seed = 21
	var img := Image.create_empty(HW, HH, false, Image.FORMAT_RGBA8)

	var skin: Array[Color] = [Color("#2e2c34"), Color("#55535c"), Color("#86838a"), Color("#b9b2ae")]
	var rags: Array[Color] = [Color("#150f1a"), Color("#261b2b"), Color("#3b2c40"), Color("#52405a")]
	var pants: Array[Color] = [Color("#0e0b12"), Color("#181320"), Color("#241c2e"), Color("#31283d")]
	var green: Array[Color] = [Color("#1c2e1e"), Color("#2c4d30"), Color("#4a7636"), Color("#82a243")]
	var brain: Array[Color] = [Color("#4a1830"), Color("#7e2f50"), Color("#b04b73"), Color("#dc87a3")]
	var lip: Array[Color] = [Color("#4a0e2a"), Color("#8f1d4a"), Color("#c23366"), Color("#ef6f90")]
	var maw: Array[Color] = [Color("#1a0510"), Color("#2a0818"), Color("#3a0a1e"), Color("#4a0e2a")]
	var hsclera: Array[Color] = [Color("#6b6258"), Color("#a89f8e"), Color("#d6cdb8"), Color("#f2ead4")]
	var fsclera: Array[Color] = [Color("#b08a22"), Color("#d8b83a"), Color("#ecd85c"), Color("#fff3a0")]
	if coiled:
		fsclera = [Color("#8a1a1a"), Color("#c23030"), Color("#e85a5a"), Color("#ff9a9a")]
	var tongue: Array[Color] = [Color("#5a1030"), Color("#a02550"), Color("#d04870"), Color("#f08aa8")]
	var black: Array[Color] = [Color.BLACK, Color.BLACK, Color.BLACK, Color.BLACK]
	var ivory := Color("#ece5c4")

	# legs and feet
	_ell(img, 20, 51, 7, 7, pants)
	_ell(img, 32, 51, 7, 7, pants)
	_ell(img, 17, 57, 6, 2, black)
	_ell(img, 35, 57, 6, 2, black)

	# ragged shirt, a torn patch showing skin
	_ell(img, 26, 46, 17, 9, rags)
	_ell(img, 34, 50, 5, 4, black)
	for r in 3:
		_line(img, Vector2(30, 48 + r * 2), Vector2(38, 48 + r * 2), skin[2], 1)
	_line(img, Vector2(34, 47), Vector2(34, 53), skin[1], 1)
	for p in [Vector2i(28, 46), Vector2i(29, 45), Vector2i(34, 47), Vector2i(35, 49), Vector2i(20, 49), Vector2i(19, 47)]:
		_put(img, p.x, p.y, rags[0])

	# arms: too long, hanging, fingers dragging
	for side in [-1, 1]:
		var sx: int = 26 + side * 19
		var pts: Array[Vector2] = [Vector2(sx, 40), Vector2(sx + side * 2, 49), Vector2(sx + side, 54)]
		for i in 2:
			_line(img, pts[i], pts[i + 1], skin[1], 3)
		for i in 2:
			_line(img, pts[i] + Vector2(0, 0), pts[i + 1] + Vector2(0, 0), skin[2], 1)
		_ell(img, sx + side, 55, 2, 2, skin)
		for k in 3:
			_put(img, sx + side - 1 + k, 57, skin[2])

	# neck
	_ell(img, 26, 41, 6, 4, skin)

	# the frog's hind legs clamp over his shoulders, feet draped on his chest
	_ell(img, 11, 37, 6, 5, green)
	_ell(img, 41, 37, 6, 5, green)
	_ell(img, 14, 44, 4, 3, green)
	_ell(img, 38, 44, 4, 3, green)
	for t in 3:
		_put(img, 12 + t * 2, 47, green[3])
		_put(img, 34 + t * 2, 47, green[3])

	# the frog's body rides behind and above the head
	_ell(img, 26, 8, 13, 7, green)
	for n in 12:
		var x := rng.randi_range(13, 39)
		var y := rng.randi_range(1, 14)
		if _solid(img, x, y):
			_put(img, x, y, green[0])
			_put(img, x - 1, y - 1, green[3])
	_eye(img, 15, 4, fsclera, green, coiled)
	_eye(img, 37, 4, fsclera, green, coiled)
	# its grin, wide and wrong
	for x in range(15, 38):
		var gy := 10 + roundi(2.0 * (1.0 - pow((x - 26) / 11.0, 2.0)))
		_put(img, x, gy, Color("#14080c"))
		if x % 2 == 1:
			_put(img, x, gy + 1, ivory)

	# the man's head
	_ell(img, 26, 29, 11, 12, skin)
	# stringy hair and ears
	for hx in [15, 16, 36, 37]:
		_line(img, Vector2(hx, 21), Vector2(hx - 1 + (hx % 2) * 2, 38), Color("#1a1418"), 1)
	_put(img, 14, 30, skin[1])
	_put(img, 14, 31, skin[1])
	_put(img, 38, 30, skin[1])
	_put(img, 38, 31, skin[1])

	# the frog's front limbs curve down and dig into his skull
	for side in [-1, 1]:
		var lp: Array[Vector2] = [Vector2(26 + side * 12, 9), Vector2(26 + side * 16, 17), Vector2(26 + side * 11, 26)]
		for i in 2:
			_line(img, lp[i], lp[i + 1], green[1], 3)
		for i in 2:
			_line(img, lp[i] + Vector2(-side, 0), lp[i + 1] + Vector2(-side, 0), green[3], 1)
		for k in 3:
			_put(img, int(lp[2].x) - side * k, int(lp[2].y) + 2 + (k % 2), green[3])

	# eyes: rolled back, mismatched
	_ell(img, 21, 29, 4, 4, black)
	_ell(img, 21, 29, 3, 3, hsclera)
	_ell(img, 31, 29, 4, 4, black)
	_ell(img, 31, 29, 3, 3, hsclera)
	if coiled:
		for p in [Vector2i(19, 29), Vector2i(23, 28), Vector2i(21, 31), Vector2i(30, 28), Vector2i(33, 30), Vector2i(31, 31)]:
			_put(img, p.x, p.y, Color("#a01818"))
	else:
		# vacant, not looking at the same thing
		for p in [Vector2i(20, 30), Vector2i(21, 30), Vector2i(20, 31), Vector2i(32, 29), Vector2i(33, 29), Vector2i(33, 28)]:
			_put(img, p.x, p.y, Color.BLACK)
	# nose
	for p in [Vector2i(26, 31), Vector2i(26, 32), Vector2i(25, 33), Vector2i(27, 33)]:
		_put(img, p.x, p.y, skin[0])

	# mouth hanging open
	if coiled:
		_ell(img, 26, 39, 6, 6, black)
		for x in range(21, 32, 2):
			_put(img, x, 34, ivory)
		for x in [23, 26, 29]:
			_put(img, x, 43, ivory)
		_ell(img, 26, 48, 3, 7, tongue)
		_put(img, 26, 54, tongue[3])
	else:
		_ell(img, 26, 38, 5, 3, black)
		for x in range(22, 31, 2):
			_put(img, x, 36, ivory)
		for x in [23, 26, 29]:
			_put(img, x, 40, ivory)
	var drool_len := 9 if coiled else 6
	for k in drool_len:
		_put(img, 31, 41 + k, Color("#8fd6e8"))

	# the crown of his skull is open: brain, with the sucker seated in it
	_ell(img, 26, 21, 12, 6, brain)
	for n in 6:
		var x := rng.randi_range(17, 35)
		var y := rng.randi_range(17, 24)
		_line(img, Vector2(x, y), Vector2(x + 3, y + rng.randi_range(-1, 1)), brain[0], 1)
	var sr := 11 if coiled else 9
	var sry := 6 if coiled else 5
	_ell(img, 26, 20, sr, sry, lip)
	_ell(img, 26, 20, sr - 3, sry - 2, maw)
	_ell(img, 26, 20, 2, 1, black)
	var tn := 18 if coiled else 12
	for a in tn:
		var t := float(a) / float(tn) * TAU
		_put(img, roundi(26.0 + cos(t) * (sr - 3.5)), roundi(20.0 + sin(t) * (sry - 2.5)), ivory)

	# cords from the sucker down into his brain: eyes, forehead
	var cdark := Color("#4a0820") if coiled else Color("#2a0818")
	var chi := Color("#ff6a8a") if coiled else Color("#e04870")
	var w := 2 if coiled else 1
	var c1: Array[Vector2] = [Vector2(20, 24), Vector2(18, 26), Vector2(18, 29)]
	var c2: Array[Vector2] = [Vector2(32, 24), Vector2(34, 26), Vector2(34, 29)]
	var c3: Array[Vector2] = [Vector2(26, 25), Vector2(26, 27)]
	_cord(img, c1, cdark, chi, w)
	_cord(img, c2, cdark, chi, w)
	_cord(img, c3, cdark, chi, w)
	for p in [Vector2i(23, 25), Vector2i(23, 27), Vector2i(29, 25), Vector2i(29, 28), Vector2i(22, 25), Vector2i(30, 26)]:
		_put(img, p.x, p.y, Color("#5a3550"))

	return _outline(img, Color("#0d0a10"))
