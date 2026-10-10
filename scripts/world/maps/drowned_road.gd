extends "res://scripts/world/map.gd"
## The drowned road north of Hollowell (dread): planks and stilts across the fen in morning fog.
## A Salt Guild waystation at the fork; Old Gristle on a mile-stone, friendly, every offer a trap;
## his "shortcut" through the leech shallows; the old road's rotten planks; and the Mouther lying in
## the peat where both ways meet. See docs/story.md (act one, the road there).
## Flags: road_seen, met_gristle, gristle_drink, leeches_done, mouther_done.

const Data := preload("res://scripts/data.gd")
const GRISTLE := "Old Gristle"
const GRISTLE_PITCH := 0.62

const LAYOUT := [
	"~~~~~~~~~~~~~~~|~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~|~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~|~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~,,,,,.,,,,~~~~~~~~~~~~",
	"~~~~~~~~,,...........,,~~~~~~~~~",
	"~~~~~~,,...............,,~~~~~~~",
	"~~~~~,....................,~~~~~",
	"~~~~,......................,~~~~",
	"~~~~,......................,~~~~",
	"~~~~,......................,~~~~",
	"~~~~~,....................,~~~~~",
	"~~~~~,,..................,,~~~~~",
	"~~~~ss,,,,............,,,~~~~~~~",
	"~~~sss~~~~~~~~~~~~~~~|~~~~~~~~~~",
	"~~ssss~~~~~~~~~~~~~~~|~~~~~~~~~~",
	"~~sss~~~~~~~~~~~~~~~~|~~~~~~~~~~",
	"~~ss~~~~~~~~~~~~~~~~xpx~~~~~~~~~",
	"~~sss~~~~~~~~~~~~~~~xpx~~~~~~~~~",
	"~~~sss~~~~~~~~~~~~~~ppx~~~~~~~~~",
	"~~ssssss~~~~~~~~~~~~pxx~~~~~~~~~",
	"~ssss~sss~~~~~~~~~~~ppp~~~~~~~~~",
	"~sss~~~ss~~~~~~~~~~~xxp~~~~~~~~~",
	"~~sss~sss~~~~~~~~~~~xpp~~~~~~~~~",
	"~~~sssss~~~~~~~~~~~~xpx~~~~~~~~~",
	"~~~~sss~~~~~~~~~~~~~~|~~~~~~~~~~",
	"~~~~~sss~~~~~~~~~~~~~|~~~~~~~~~~",
	"~~~~~~sss~~~~~~~~~~~~|~~~~~~~~~~",
	"~~~~~~~ss,,,,,,,,,,,,.,,~~~~~~~~",
	"~~~~~~~~,,..............,,~~~~~~",
	"~~~~~~~,..................,~~~~~",
	"~~~~~~,....................,~~~~",
	"~~~~~~,....................,~~~~",
	"~~~~~~,....................,~~~~",
	"~~~~~~~,,................,,~~~~~",
	"~~~~~~~~~,,,,,,.,,,,,,,,~~~~~~~~",
	"~~~~~~~~~~~~~~~|~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~|~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~|~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~|~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
]

const CIRCLE := Vector2i(15, 31)        # the waystation's post
const PUZZLE_ENTRY := Vector2i(21, 24)  # the last sound board before the rotten stretch
const MOUTHER_AT := Vector2i(14, 8)     # where it lies in the peat (2x1)
const POOL := Rect2i(1, 18, 9, 6)       # the shallows where the leeches wait
const POINTS := {"self": "himself", "gristle": "Old Gristle"}

var gristle: Actor
var mouther_lying: Sprite2D
var mouther: Actor


func build() -> void:
	lay(PackedStringArray(LAYOUT), Tiles.FEN)
	darken(1.0, Color(0.84, 0.87, 1.0))    # the same grey morning he left Hollowell in
	var mist := preload("res://scripts/world/fog.gd").new()
	add_child(mist)
	mist.setup(Vector2(size_px()), 0.42)
	spawns["south"] = [Vector2i(15, 38), Vector2i.UP]
	spawns["circle"] = [CIRCLE + Vector2i(0, 1), Vector2i.UP]
	walls[Vector2i(15, 39)] = true

	prop(load("res://art/world/salt_circle.png"), CIRCLE, Vector2i.ONE, true, Vector2i(0, 7))
	examine[CIRCLE] = rest
	prop(load("res://art/world/signpost.png"), Vector2i(12, 28))
	examine[Vector2i(12, 28)] = read_sign
	prop(load("res://art/world/milestone.png"), Vector2i(19, 30))
	examine[Vector2i(19, 30)] = func() -> void:
		await world.narrate("A mile-stone. Someone has notched it thirty times, and started a thirty-first.")
	for t in [[Vector2i(24, 28), 0], [Vector2i(25, 31), 1], [Vector2i(7, 6), 1], [Vector2i(25, 6), 0], [Vector2i(9, 32), 1]]:
		prop(load("res://art/world/dead_tree_%d.png" % t[1]), t[0])
	var reed_spots := [Vector2i(10, 33), Vector2i(23, 33), Vector2i(17, 27), Vector2i(6, 11), Vector2i(22, 11),
		Vector2i(11, 3), Vector2i(19, 4), Vector2i(26, 9), Vector2i(5, 8)]
	for i in reed_spots.size():
		prop(load("res://art/world/reeds_%d.png" % (i % 3)), reed_spots[i], Vector2i.ONE, false)

	if not world.flags.get("mouther_done", false):
		gristle = person("res://art/world/gristle.png", Vector2i(20, 30), Vector2i.DOWN, 2, Vector2i(16, 24))
		gristle.turns_to_talk = false
		gristle.talk = talk_gristle
		landmarks["gristle"] = gristle
		if not world.flags.get("met_gristle", false):
			for x in range(9, 25):
				triggers[Vector2i(x, 33)] = gristle_calls
		mouther_lying = prop(load("res://art/world/mouther_lying.png"), MOUTHER_AT, Vector2i(2, 1))
		for y in range(5, 13):
			for x in range(10, 21):
				var c := Vector2i(x, y)
				if c.distance_to(Vector2(MOUTHER_AT) + Vector2(0.5, 0)) <= 3.0 and not blocked(c):
					triggers[c] = mouther_rises
	for y in rows.size():
		for x in rows[y].length():
			var c := Vector2i(x, y)
			if rows[y][x] == "x":
				triggers[c] = plank_gives
			elif rows[y][x] == "s" and POOL.has_point(c) and not world.flags.get("leeches_done", false):
				triggers[c] = leeches
	triggers[Vector2i(15, 1)] = road_north


func arrive(spawn: String) -> void:
	await world.reveal(0.8)
	if spawn == "south" and not world.flags.get("road_seen", false):
		world.flags["road_seen"] = true
		await world.narrate("North of Hollowell the road runs out across the fen on planks, and stilts, and hope.")
		world.hint("Fog on the water. Mind the planks.", 4.0)


# --------------------------------------------------------------------------------------------
# the waystation and the sign
# --------------------------------------------------------------------------------------------

func rest() -> void:
	await world.narrate("A ring of salt, kept white. Riders won't cross it. Somebody of the Guild keeps this place.")
	await world.narrate("Rest inside the salt?")
	if (await world.ask())["g"] != "nod":
		return
	await world.cover(0.8)
	world.hero_state = {}
	await world.narrate("He sleeps a while inside the ring. Nothing comes near.")
	await world.reveal(0.8)


func read_sign() -> void:
	await world.narrate("HOLLOWELL, south. TALLOWMOUTH, north.")
	await world.narrate("Scratched underneath: THE OLD ROAD EATS PEOPLE. Under that, another hand: SO DOES THE LEFT.")


# --------------------------------------------------------------------------------------------
# Old Gristle
# --------------------------------------------------------------------------------------------

func gristle_calls() -> void:
	for x in range(9, 25):
		triggers.erase(Vector2i(x, 33))
	await world.say(GRISTLE, "Ho there! Another one walking north!", GRISTLE_PITCH)
	await world.say(GRISTLE, "Come and sit, rookie. Old Gristle doesn't bite. Much.", GRISTLE_PITCH)


func laugh() -> void:
	gristle.sprite.frame = 1
	await world.caption("Something under his coat laughs, a beat after he does.", 1.8)
	gristle.sprite.frame = 0


func talk_gristle() -> void:
	player.face_toward(gristle)
	if world.flags.get("met_gristle", false):
		if world.flags.get("leeches_done", false):
			await world.say(GRISTLE, "Shallows a bit lively, were they? Ha! Builds character.", GRISTLE_PITCH)
		else:
			await world.say(GRISTLE, "Still here? The left fork, rookie. Through the shallows. Off you go.", GRISTLE_PITCH)
		await laugh()
		return
	world.flags["met_gristle"] = true
	for x in range(9, 25):
		triggers.erase(Vector2i(x, 33))
	await world.say(GRISTLE, "Another rookie for the Examination, by the look of you. Am I wrong?", GRISTLE_PITCH)
	var a: Dictionary = await world.ask(POINTS)
	match a["g"]:
		"nod":
			await world.say(GRISTLE, "Ha! Never wrong. I can smell a rookie a mile off. Fen-stink and hope.", GRISTLE_PITCH)
		"shake":
			await world.say(GRISTLE, "No? Walking north at dawn with a Guild face on? Liar. I like liars.", GRISTLE_PITCH)
		"shrug":
			await world.say(GRISTLE, "Don't know where you're going? That's the spirit. Nobody does.", GRISTLE_PITCH)
		"show":
			if a["item"] == "poster":
				await world.say(GRISTLE, "The Guild's riddle! Hungry fed and never full. That's Plenty, rookie.", GRISTLE_PITCH)
				await world.say(GRISTLE, "Everybody knows. Well. Everybody who's been thirty times.", GRISTLE_PITCH)
			elif a["item"] == "lantern":
				await world.say(GRISTLE, "A lamp! Put that out before the Mere, rookie. Trust me on that one.", GRISTLE_PITCH)
			else:
				await world.say(GRISTLE, "Pennies? Keep them. The ferrywoman takes pennies.", GRISTLE_PITCH)
		"point":
			if a["at"] == "gristle":
				await world.say(GRISTLE, "Me? Oh, I'm going too. They know my face at the door by now.", GRISTLE_PITCH)
			else:
				await world.say(GRISTLE, "You, aye. A rookie. It's all over you, like fen-stink.", GRISTLE_PITCH)
		_:
			await world.say(GRISTLE, "The quiet sort. The quiet ones never ask for help, so they never get any.", GRISTLE_PITCH)
			await world.say(GRISTLE, "Lucky for you I'm here.", GRISTLE_PITCH)
	await world.say(GRISTLE, "This'll be my thirty-first Examination. Thirty-one! I'm practically furniture.", GRISTLE_PITCH)
	await laugh()
	await world.say(GRISTLE, "A nip of eel-wine for the road? Puts hair on your tongue.", GRISTLE_PITCH)
	var drink: Dictionary = await world.ask(POINTS)
	if drink["g"] == "nod":
		world.flags["gristle_drink"] = true
		await world.caption("It tastes of pennies, and of something worse. His stomach turns over.", 2.4)
		var hp: int = int(world.hero_state.get("hp", Data.HERO["max_hp"]))
		world.hero_state["hp"] = maxi(1, hp - 15)
		await world.say(GRISTLE, "Ha! Strong stuff. Takes some getting used to.", GRISTLE_PITCH)
		await laugh()
	else:
		await world.say(GRISTLE, "Suit yourself. More for me.", GRISTLE_PITCH)
		await world.caption("He pours it into the mouth under his coat. It drinks.", 2.0)
	await world.say(GRISTLE, "Free advice, rookie. Take the left fork, through the shallows.", GRISTLE_PITCH)
	await world.say(GRISTLE, "Shorter. Drier than it looks. The old road eats people, you know.", GRISTLE_PITCH)
	match (await world.ask(POINTS))["g"]:
		"nod":
			await world.say(GRISTLE, "Good lad. Off you go. I'll catch you up.", GRISTLE_PITCH)
			await laugh()
		"shake":
			await world.say(GRISTLE, "Suit yourself. Don't say Old Gristle never told you.", GRISTLE_PITCH)
		_:
			await world.say(GRISTLE, "Think on it. I'll be here. I'm always here.", GRISTLE_PITCH)


# --------------------------------------------------------------------------------------------
# the roads
# --------------------------------------------------------------------------------------------

func plank_gives() -> void:
	world.sfx.play("splash")
	await shake(3.0, 0.3)
	await world.narrate("The plank gives way! He goes into the black water to the waist.")
	await world.cover(0.5)
	player.place(PUZZLE_ENTRY)
	player.face(Vector2i.UP)
	await world.reveal(0.5)
	await world.narrate("He drags himself back onto the boards, soaked. The rotten ones are darker. Mossier.")


func leeches() -> void:
	for c: Vector2i in triggers.keys():
		if triggers[c] == leeches:
			triggers.erase(c)
	await world.narrate("Something brushes his legs in the shallows. Then something else.")
	if await fight(["penny_leech", "penny_leech", "penny_leech"], {}, "circle") != "won":
		return
	world.flags["leeches_done"] = true
	world.items["pennies"] = "wishing pennies"
	await world.narrate("Where they died, pennies glint in the mud. Hollowell's wishes, green with the fen.")
	await world.caption("He takes a handful of wishing pennies.", 1.8)


func mouther_rises() -> void:
	for c: Vector2i in triggers.keys():
		if triggers[c] == mouther_rises:
			triggers.erase(c)
	player.face_toward_pos(mouther_lying.position)
	await world.narrate("A body lies in the peat, face to the sky, its jaw hanging open.")
	await world.caption("Its jaw works. No sound comes out.", 2.0)
	world.box.close()
	world.sfx.play("thud")
	await shake(1.0, 0.2)
	mouther_lying.hide()
	walls.erase(MOUTHER_AT)
	walls.erase(MOUTHER_AT + Vector2i.RIGHT)
	mouther = person("res://art/world/mouther.png", MOUTHER_AT, Vector2i.DOWN, 1, Vector2i(16, 24))
	mouther.turns_to_talk = false
	await world.wait(0.8)
	await world.caption("It stands up, crooked, and turns its open mouth toward him.", 2.0)
	var outcome := await fight(["mouther"], {}, "circle")
	if outcome != "won":
		return
	world.flags["mouther_done"] = true
	vacate(mouther.cell, mouther)
	mouther.queue_free()
	await world.narrate("Where it lay, the peat closes over, like a mouth.")


func road_north() -> void:
	await world.narrate("The road runs on north across the fen, toward Tallowmouth and the Black Mere.")
	await world.cover(1.2)
	await world.narrate("The drowned road. The end, for now.")
	await world.narrate("Next: Tallowmouth, the ferrywoman, and Old Iron.")
	get_tree().change_scene_to_file("res://title.tscn")
