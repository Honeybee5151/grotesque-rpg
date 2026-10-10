extends "res://scripts/world/map.gd"
## The flooded cave under Hollowell's well (dread). Odo's lantern still burns on a rock; the Host
## lurches out of the dark beyond it. Sets the flags host_done and odo_body (where he fell).

const LAYOUT := [
	"########################",
	"########################",
	"##...###################",
	"##....##################",
	"###.....################",
	"####.....###############",
	"#####......####...######",
	"######...........,,..###",
	"#######.........,~~,...#",
	"########........,~~~,..#",
	"########.....,,,~~~~,..#",
	"#######..........,,,...#",
	"########...............#",
	"##########..........####",
	"########################",
]

const SHAFT := Vector2i(3, 2)
const LANTERN := Vector2i(13, 9)
const HOST_START := Vector2i(19, 12)

var lantern: Sprite2D
var host: Actor
var _lantern_light := -1


func build() -> void:
	lay(PackedStringArray(LAYOUT), Tiles.CAVE)
	darken(0.1)
	hero_glow = 0.45
	spawns["shaft"] = [SHAFT, Vector2i.DOWN]
	prop(load("res://art/world/rungs.png"), Vector2i(3, 1), Vector2i.ONE, true, Vector2i(0, -1))
	var rocks := [[Vector2i(5, 3), 0], [Vector2i(8, 5), 1], [Vector2i(16, 6), 2], [Vector2i(21, 8), 0], [Vector2i(9, 12), 1]]
	for r in rocks:
		prop(load("res://art/world/stalagmite_%d.png" % r[1]), r[0])
	light.add(at(SHAFT, -14), 34.0, 0.8)                     # grey light falling down the shaft
	if world.flags.get("host_done", false):
		lay_body(world.flags.get("odo_body", Vector2i(18, 12)))
	if world.items.has("lantern"):
		prop(load("res://art/world/rock.png"), LANTERN)
	else:
		lantern = prop(load("res://art/world/lantern_rock.png"), LANTERN)
		_lantern_light = light.add(at(LANTERN, -4), 60.0, 1.0, true)
		examine[LANTERN] = take_lantern
	examine[Vector2i(3, 1)] = climb_up
	for c in [Vector2i(17, 9), Vector2i(18, 9), Vector2i(17, 8), Vector2i(18, 10)]:
		examine[c] = func() -> void:
			await world.narrate("The water is black and still. Something under it is still too.")
	if not world.flags.get("host_done", false):
		for y in range(7, 13):
			for x in range(10, 17):
				if Vector2i(x, y).distance_to(LANTERN) <= 2.3 and not blocked(Vector2i(x, y)):
					triggers[Vector2i(x, y)] = host_comes


func arrive(_spawn: String) -> void:
	await world.reveal(0.8)
	if not world.flags.get("cave_seen", false):
		world.flags["cave_seen"] = true
		await world.narrate("The bottom of the well opens into a cave. Water drips. Far off, a light.")


func host_comes() -> void:
	triggers.clear()
	player.face_toward(lantern)
	await world.narrate("Odo's lantern, set down carefully on a rock. Still lit.")
	world.box.close()
	await world.wait(0.4)
	world.sfx.play("drip")
	await world.wait(1.0)
	world.sfx.play("thud")
	await shake(1.0, 0.2)
	host = person("res://art/world/host_walk.png", HOST_START, Vector2i.DOWN, 2, Vector2i(24, 26))
	host.turns_to_talk = false
	await world.wait(0.8)
	# it lurches out of the dark at him: a step, a pause, like something still learning the legs
	for i in 14:
		var to := player.cell - host.cell
		if absi(to.x) + absi(to.y) <= 1:
			break
		var d := Vector2i(signi(to.x), 0) if absi(to.x) >= absi(to.y) else Vector2i(0, signi(to.y))
		var alt := Vector2i(0, signi(to.y)) if d.x != 0 else Vector2i(signi(to.x), 0)
		if not host.step(d) and (alt == Vector2i.ZERO or not host.step(alt)):
			break
		host.face(Vector2i.DOWN)
		await host.arrived
		await world.wait(0.22)
	player.face_toward(host)
	await world.wait(0.3)
	var result: Dictionary = await world.battle(["host"], {
		"intro": ["Odo staggers out of the dark.", "Something wet rides his back.", "He says nothing. For once."],
		"bg": "cave",
		"mercy": true,
		"can_run": false,
	})
	var fell := host.cell
	vacate(host.cell, host)
	host.queue_free()
	host = null
	if result.get("outcome", "") != "won":
		# the tutorial can't be lost (mercy); if it ever is, the frog drags him off to try again
		await world.narrate("The frog drags Odo back into the dark. It will come again.")
		for c in [Vector2i(12, 10), Vector2i(13, 10), Vector2i(14, 10), Vector2i(12, 9)]:
			triggers[c] = host_comes
		return
	world.flags["host_done"] = true
	world.flags["odo_body"] = fell
	lay_body(fell)


## Odo where he fell: two free cells side by side at or next to `c` (never under the hero).
func lay_body(c: Vector2i) -> void:
	var at_cell := c
	for o: Vector2i in [Vector2i.ZERO, Vector2i.LEFT, Vector2i.DOWN, Vector2i(-1, 1), Vector2i.UP, Vector2i(1, 1), Vector2i(2, 0)]:
		var a := c + o
		if not blocked(a) and not blocked(a + Vector2i.RIGHT):
			at_cell = a
			break
	prop(load("res://art/world/odo_dead.png"), at_cell, Vector2i(2, 1))
	for o: Vector2i in [Vector2i(2, 1), Vector2i(2, 0), Vector2i(0, 1), Vector2i(-1, 0)]:
		if not blocked(at_cell + o):
			prop(load("res://art/world/frog_spent.png"), at_cell + o, Vector2i.ONE, false)
			break
	for x in 2:
		examine[at_cell + Vector2i(x, 0)] = look_odo


func look_odo() -> void:
	await world.narrate("He lies face down. His mouth is open, as if he finally ran out of things to say.")


func take_lantern() -> void:
	if not world.flags.get("host_done", false):
		await world.narrate("Odo's lantern, set down carefully on a rock. Still lit.")
		return
	await world.narrate("He takes Odo's lantern.")
	world.items["lantern"] = "Odo's lantern"
	lantern.texture = load("res://art/world/rock.png")
	light.set_strength(_lantern_light, 0.0)
	examine.erase(LANTERN)
	hero_glow = 0.9
	light.set_strength(_glow, 0.9)


func climb_up() -> void:
	if not world.flags.get("host_done", false):
		await world.narrate("The rungs go back up to the light. Not without Odo.")
		return
	await world.narrate("The rungs go back up to the light. Climb up?")
	if (await world.ask())["g"] == "nod":
		world.sfx.play("creak")
		world.go("hollowell", "well")
