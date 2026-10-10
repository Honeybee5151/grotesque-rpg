extends "res://scripts/world/map.gd"
## Hollowell, in the Sallow Fen (dread): the prologue. A peat island of stilt-houses around one deep
## well, black water on every side. Odo goes down the well, the hero minds the rope, and comes back
## up alone to Moth's question. See docs/story.md.
## Flags: opened, met_odo, odo_down, rope_cut, host_done (set in the cave), moth_read.

const ODO := "Odo"
const MOTH := "Moth"
const ODO_PITCH := 0.8
const MOTH_PITCH := 1.45
const WELL := Vector2i(14, 9)          # top-left of the well's 2x2 footprint
const ODO_SPOT := Vector2i(14, 11)
const MOTH_DOOR := Vector2i(7, 6)

const LAYOUT := [
	"~~~~~~~~~~~~~~~|~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~|~~~~~~~~~~~~~~",
	"~~~~~~~~,,,,,,,.,,,,,,~~~~~~~~",
	"~~~~~~,,,..............,,~~~~~",
	"~~~~~,,.................,~~~~~",
	"~~~~~,..................,,~~~~",
	"~~~~,....................,~~~~",
	"~~~~,....................,~~~~",
	"~~~~,.........oooo........,~~~",
	"~~~~,........oooooo.......,~~~",
	"~~~~,........oooooo.......,~~~",
	"~~~~,,........oooo.......,,~~~",
	"~~~~~,...................,~~~~",
	"~~~~~,,.................,,~~~~",
	"~~~~~~~,,,...........,,,~~~~~~",
	"~~~~~~~~~~,,,,,.,,,,,~~~~~~~~~",
	"~~~~~~~~~~~~~~~|~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~|~~~~~~~~~~~~~~",
	"~~~~~~~~~~~=====~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
]

# what the hero can point at while talking here
const POINTS := {"self": "himself", "well": "the well", "odo": "Odo"}

var odo: Actor
var moth: Actor
var _odo_light := -1


func build() -> void:
	lay(PackedStringArray(LAYOUT), Tiles.FEN)
	darken(0.42)
	spawns["start"] = [Vector2i(11, 18), Vector2i.RIGHT]
	spawns["well"] = [Vector2i(15, 11), Vector2i.DOWN]
	walls[Vector2i(15, 0)] = true

	prop(load("res://art/world/house_odo.png"), Vector2i(6, 4), Vector2i(4, 2))
	prop(load("res://art/world/house_shut.png"), Vector2i(19, 4), Vector2i(4, 2))
	prop(load("res://art/world/house_dark.png"), Vector2i(20, 11), Vector2i(4, 2))
	prop(load("res://art/world/well.png"), WELL, Vector2i(2, 2))
	prop(load("res://art/world/lamp_post.png"), Vector2i(16, 15))
	var reed_spots := [Vector2i(5, 6), Vector2i(4, 9), Vector2i(24, 3), Vector2i(26, 8), Vector2i(8, 14),
		Vector2i(22, 14), Vector2i(11, 15), Vector2i(20, 15), Vector2i(6, 12), Vector2i(17, 2)]
	for i in reed_spots.size():
		prop(load("res://art/world/reeds_%d.png" % (i % 3)), reed_spots[i], Vector2i.ONE, false)

	# lights: Odo's window and door, the shuttered window's crack, the lamp post, the well's lantern
	light.add(Vector2(141, 77), 30.0, 0.85, true)
	light.add(Vector2(129, 84), 22.0, 0.7, true)
	light.add(Vector2(354, 77), 16.0, 0.6)
	light.add(Vector2(282, 230), 40.0, 0.9, true)
	light.add(Vector2(223, 140), 44.0, 0.9, true)

	examine_cells(WELL, Vector2i(2, 2), look_well)
	examine_cells(Vector2i(19, 4), Vector2i(4, 2), func() -> void:
		await world.narrate("Behind the shutters, someone holds their breath until he passes."))
	examine_cells(Vector2i(20, 11), Vector2i(4, 2), func() -> void:
		await world.narrate("Nobody lives here now. The door is nailed shut from the outside."))
	examine_cells(Vector2i(6, 4), Vector2i(4, 2), func() -> void:
		await world.narrate("Odo's house. It smells of tallow and wet rope."))
	examine[Vector2i(16, 15)] = func() -> void:
		await world.narrate("A lamp on a pole, kept lit for boats that stopped coming.")
	triggers[Vector2i(15, 1)] = north_fog

	if not world.flags.get("odo_down", false):
		odo = person("res://art/world/odo.png", ODO_SPOT, Vector2i.DOWN)
		odo.talk = talk_odo
		_odo_light = light.add(odo.position + Vector2(-5, -8), 46.0, 0.95, true)
		for x in range(6, 26):
			triggers[Vector2i(x, 13)] = odo_calls
	var waiting: bool = world.flags.get("host_done", false) and not world.flags.has("moth_read")
	moth = person("res://art/world/moth.png", Vector2i(14, 12) if waiting else MOTH_DOOR,
		Vector2i.UP if waiting else Vector2i.DOWN)
	moth.talk = talk_moth
	landmarks["well"] = Vector2(WELL.x * TILE + TILE, WELL.y * TILE + TILE)
	landmarks["moth"] = moth
	if odo != null:
		landmarks["odo"] = odo


func arrive(spawn: String) -> void:
	if spawn == "start" and not world.flags.get("opened", false):
		world.flags["opened"] = true
		await world.wait(0.8)
		await world.narrate("They pulled him out of the fen at dusk.")
		await world.narrate("He coughed up black water, and nothing else.")
		world.box.close()
		await world.reveal(1.2)
		await world.caption("(Arrows walk. Z talks, looks and answers.)", 2.5)
		return
	await world.reveal()
	if spawn == "well" and world.flags.get("host_done", false) and not world.flags.has("moth_read"):
		await moth_asks()


func _process(_delta: float) -> void:
	if odo != null and _odo_light >= 0:
		light.move(_odo_light, odo.position + Vector2(-5, -8) + Vector2(0, odo.sprite.offset.y + 23))


func examine_cells(c: Vector2i, footprint: Vector2i, ev: Callable) -> void:
	for y in footprint.y:
		for x in footprint.x:
			examine[c + Vector2i(x, y)] = ev


# --------------------------------------------------------------------------------------------
# Odo
# --------------------------------------------------------------------------------------------

func odo_calls() -> void:
	for x in range(6, 26):
		triggers.erase(Vector2i(x, 13))
	odo.face_toward(player)
	await world.say(ODO, "Ho! The drowned man walks!", ODO_PITCH)
	await world.say(ODO, "Come here, come here. Let me look at you.", ODO_PITCH)


func talk_odo() -> void:
	if world.flags.get("met_odo", false):
		return
	world.flags["met_odo"] = true
	for x in range(6, 26):
		triggers.erase(Vector2i(x, 13))
	player.face_toward(odo)
	await world.say(ODO, "They said you'd sleep till Sunday. You look worse than that.", ODO_PITCH)
	await world.say(ODO, "I'm Odo. I keep the well. Well... the well keeps me.", ODO_PITCH)
	await world.say(ODO, "Can you talk, or did the fen keep that too?", ODO_PITCH)
	match (await world.ask(POINTS))["g"]:
		"nod":
			await world.say(ODO, "Go on, then.", ODO_PITCH)
			await world.wait(0.9)
			await world.say(ODO, "...Ha! A liar, and a quiet one. I like you already.", ODO_PITCH)
		"shake":
			await world.say(ODO, "Kept it, did it. The fen's a greedy old mouth.", ODO_PITCH)
		"shrug":
			await world.say(ODO, "Don't know? Fair. Nor do I, most mornings.", ODO_PITCH)
		"point":
			await world.say(ODO, "...Was that an answer? I'll take it as one. I take most things.", ODO_PITCH)
		_:
			await world.say(ODO, "...Right. My wife used to go quiet like that. Meant I was wrong.", ODO_PITCH)
	await world.say(ODO, "Never mind. I talk enough for a parish. Here's the trouble.", ODO_PITCH)
	await world.say(ODO, "The water's gone bad. Tastes of pennies.", ODO_PITCH)
	await world.say(ODO, "Last night the bucket came up full of spawn. Black spawn.", ODO_PITCH)
	await world.say(ODO, "So I'm going down. Somebody has to, and I'm the somebody.", ODO_PITCH)
	await world.say(ODO, "You'll mind the rope? One tug, I'm fine. Two tugs, haul me up.", ODO_PITCH)
	var a: Dictionary = await world.ask(POINTS)
	match a["g"]:
		"nod":
			await world.say(ODO, "Good man. One tug fine, two tugs haul. Simple as soup.", ODO_PITCH)
		"shake":
			await world.say(ODO, "No? ...That was a yes. I've decided. I'm good at deciding for people.", ODO_PITCH)
		"shrug":
			await world.say(ODO, "That's a yes where I'm from. Most things are.", ODO_PITCH)
		"point":
			match a["at"]:
				"well": await world.say(ODO, "Aye, down there. You're a quick one.", ODO_PITCH)
				"self": await world.say(ODO, "You, yes. Who else? Moth's ten and the rest are cowards.", ODO_PITCH)
				_: await world.say(ODO, "Me down there, you up here. You've got it.", ODO_PITCH)
		_:
			await world.say(ODO, "Silence is a yes. That's the law. I just made it.", ODO_PITCH)
	await world.say(ODO, "Moth! Stay in the door. Your da's going fishing.", ODO_PITCH)
	await odo_goes_down()


func odo_goes_down() -> void:
	world.flags["odo_down"] = true
	world.box.close()
	odo.face(Vector2i.UP)
	await world.wait(0.4)
	# he climbs onto the rim and sinks into the shaft; the well's sprite covers him as he goes
	world.sfx.play("creak")
	vacate(odo.cell, odo)
	var tw := create_tween()
	tw.tween_property(odo, "position", Vector2(WELL.x * TILE + TILE, 157), 0.35)
	await tw.finished
	await world.wait(0.3)
	tw = create_tween()
	tw.tween_property(odo.sprite, "offset:y", odo.sprite.offset.y + 26.0, 1.4)
	await tw.finished
	light.set_strength(_odo_light, 0.0)
	odo.queue_free()
	odo = null
	await world.wait(0.6)
	await rope()


func rope() -> void:
	player.face(Vector2i.UP)
	await world.caption("The rope pays out through his hands...", 1.8)
	world.sfx.play("creak")
	await world.caption("...and stops.", 1.4)
	await world.wait(1.2)
	await tug("One tug.")
	await world.wait(1.6)
	await tug("One tug.")
	await world.wait(2.4)
	await tug("Two tugs!", 2)
	await world.choose([{"label": "Haul!", "value": true}])
	world.sfx.play("splash")
	await shake(3.0, 0.3)
	await world.narrate("He hauls. The rope comes up fast. Too fast. Too light.")
	await world.narrate("Its end is wet, and warm, and bitten through.")
	world.flags["rope_cut"] = true
	moth.face(Vector2i.RIGHT)
	await world.say(MOTH, "Da?", MOTH_PITCH)


func tug(text: String, times := 1) -> void:
	for i in times:
		world.sfx.play("tug")
		shake(2.0, 0.15)
		await world.wait(0.25)
	await world.caption(text, 1.0)


func look_well() -> void:
	if not world.flags.get("rope_cut", false):
		await world.narrate("The well breathes out cold air. It smells of pennies.")
		return
	await world.narrate("Iron rungs go down the inside of the well, into the dark. Climb down?")
	var a: Dictionary = await world.ask({"well": "the well"})
	match a["g"]:
		"nod":
			world.sfx.play("creak")
			world.go("well_cave", "shaft")
		"point":
			await world.narrate("He points down the well. There is nobody to see it.")
		"shake":
			await world.narrate("Not yet.")
		_:
			await world.narrate("He stands at the rim, listening. Far down, something drips.")


# --------------------------------------------------------------------------------------------
# Moth
# --------------------------------------------------------------------------------------------

func talk_moth() -> void:
	if world.flags.get("host_done", false):
		if world.flags.has("moth_read"):
			await moth_after()
		else:
			await moth_asks()
		return
	if world.flags.get("rope_cut", false):
		await world.say(MOTH, "That was Da's rope.", MOTH_PITCH)
		await world.say(MOTH, "Is he coming up?", MOTH_PITCH)
		match (await world.ask({"self": "himself", "well": "the well", "moth": "Moth"}))["g"]:
			"nod": await world.say(MOTH, "Then why's the rope like that?", MOTH_PITCH)
			"shake": await world.say(MOTH, "He is. He always comes up. He talks too much to stay anywhere.", MOTH_PITCH)
			_: await world.say(MOTH, "...Go and get him. You're the only one who isn't scared.", MOTH_PITCH)
		return
	if world.flags.get("met_moth", false):
		await world.say(MOTH, "Da talks to the well, you know. Lately it talks back.", MOTH_PITCH)
		return
	world.flags["met_moth"] = true
	await world.say(MOTH, "Da says you're a drowned man.", MOTH_PITCH)
	await world.say(MOTH, "Are you?", MOTH_PITCH)
	var a: Dictionary = await world.ask({"self": "himself", "moth": "Moth"})
	match a["g"]:
		"nod":
			await world.say(MOTH, "I knew it. You're the wrong colour for alive.", MOTH_PITCH)
		"shake":
			await world.say(MOTH, "That's what a drowned man would say. If he could say.", MOTH_PITCH)
		"shrug":
			await world.say(MOTH, "You don't know if you're dead? That's the saddest thing I ever heard.", MOTH_PITCH)
		"point":
			if a["at"] == "moth":
				await world.say(MOTH, "Me? I'm not drowned. I'm Moth. Da says it's 'cause I follow the lamp.", MOTH_PITCH)
			else:
				await world.say(MOTH, "That's not an answer. That's a finger.", MOTH_PITCH)
		_:
			await world.say(MOTH, "Drowned men don't talk. Everybody knows that.", MOTH_PITCH)
	await world.say(MOTH, "Da talks to the well, you know. Lately it talks back.", MOTH_PITCH)


## He climbed out alone. She asks, and how he answers decides what Hollowell thinks of him.
func moth_asks() -> void:
	moth.face_toward(player)
	player.face_toward(moth)
	await world.say(MOTH, "Where's my da?", MOTH_PITCH)
	var points := {"well": "the well", "self": "himself", "moth": "Moth"}
	for attempt in 3:
		var a: Dictionary = await world.ask(points)
		var g: String = a["g"]
		if g == "show":
			await world.say(MOTH, "That's his lamp.", MOTH_PITCH)
			await world.say(MOTH, "He never puts it down. Not to eat. Not to sleep.", MOTH_PITCH)
			await world.wait(0.8)
			await world.say(MOTH, "...Oh.", MOTH_PITCH)
			world.items.erase("lantern")
			await moth_ends("grief")
			return
		if g == "shake":
			await world.say(MOTH, "No. You don't get to shake your head at me.", MOTH_PITCH)
			await world.say(MOTH, "Say it. SAY it!", MOTH_PITCH)
			await world.wait(0.8)
			await world.say(MOTH, "...You can't. Can you.", MOTH_PITCH)
			await moth_ends("grief")
			return
		if g == "silent":
			await world.say(MOTH, "Say something.", MOTH_PITCH)
			await world.wait(1.0)
			await world.say(MOTH, "...That's how the doctor stood. When Mam.", MOTH_PITCH)
			await moth_ends("grief")
			return
		if g == "shrug":
			await world.say(MOTH, "You don't KNOW? You were down there!", MOTH_PITCH)
			await world.say(MOTH, "...You don't even care.", MOTH_PITCH)
			await moth_ends("cold")
			return
		if g == "point" and a["at"] == "self":
			await world.say(MOTH, "You?", MOTH_PITCH)
			await world.say(MOTH, "What did you do? What did you DO to him?", MOTH_PITCH)
			await moth_ends("blame")
			return
		if g == "point" and a["at"] == "moth":
			await world.say(MOTH, "Me? You want ME to go down there?", MOTH_PITCH)
			await world.say(MOTH, "...Where IS he?", MOTH_PITCH)
			continue
		# a nod, or pointing down the well: she hears that he's alive
		if attempt < 2:
			var hope := "He's still down there? He's alive?" if attempt == 0 \
				else "Then why didn't you bring him? Is he hurt?"
			await world.say(MOTH, hope, MOTH_PITCH)
			await world.say(MOTH, "Is he coming up?" if attempt == 0 else "Is he?", MOTH_PITCH)
	await world.say(MOTH, "DA! DA, COME UP!", MOTH_PITCH)
	await world.narrate("She calls down the well until her voice gives out. Nothing calls back.")
	await moth_ends("hope")


func moth_ends(read: String) -> void:
	world.flags["moth_read"] = read
	match read:
		"grief":
			await world.narrate("She doesn't cry. She sits by the well with the lamp and keeps it lit.")
		"cold":
			moth.face(Vector2i.UP)
			await world.narrate("She turns her back on him and watches the well instead.")
		"blame":
			await world.narrate("She runs. Doors bang all the way down the boardwalk.")
			await world.narrate("By morning all of Hollowell knows what the drowned man did.")
		"hope":
			await world.narrate("She will wait by the well tonight, and every night after.")
	await world.wait(0.6)
	await world.cover(1.2)
	await world.narrate("Hollowell. The end of the beginning.")
	await world.narrate("(Thanks for playing this far. More of the fen is coming.)")
	get_tree().change_scene_to_file("res://title.tscn")


func moth_after() -> void:
	match world.flags["moth_read"]:
		"blame": await world.say(MOTH, "Don't come near me.", MOTH_PITCH)
		"cold": await world.say(MOTH, "...", MOTH_PITCH)
		_: await world.say(MOTH, "I'm keeping it lit. In case.", MOTH_PITCH)


func north_fog() -> void:
	await world.narrate("The boardwalk runs north into the fog. Odo says the road drowns every spring.")
	await player.walk([Vector2i.DOWN])
