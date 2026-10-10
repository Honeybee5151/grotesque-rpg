extends RefCounted
## The procedural cave background behind the title screen and battles (320x180).
## Monsters are PNGs in art/monsters/<id>/ (see docs/art.md).

const BAYER := [[0, 2], [3, 1]]


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
