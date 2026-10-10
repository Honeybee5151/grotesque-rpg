extends "res://scripts/world/dev/drive.gd"
## Headless playthroughs of the prologue, for the merge checks:
##   godot --headless --path . --script res://scripts/world/dev/world_test.gd [-- story | sweep [FILTER]]
## "story" plays the two endings through to the title; "sweep" opens every gesture prompt and tries
## every answer it offers (each gesture, each point-at target, each item), then goes on with first
## choices until the hero has control again or the game is back at the title - so a branch that
## never hands control back fails as "stuck". No argument runs both. Prints one "=== WORLD:" line per
## scenario and exits 1 if any step timed out, got stuck or missed an expectation.

const HOLLOWELL_TO_CAVE := "until:They_pulled Z until:coughed Z wait:1.4 R*4 U*5 until:drowned_man_walks Z until:look_at_you Z U*1 wait:0.2 U*1 wait:0.2 L*1 Z until:sleep_till Z until:keeps_me Z until:Can_you_talk Z pick:0 until:Go_on Z until:liar Z until:parish Z until:pennies Z until:penny Z until:spawn. Z until:going_down Z until:mind_the_rope Z pick:4 until:law Z until:Moth! Z until:Two_tugs! Z until:hauls Z until:bitten Z until:Da? Z wait:0.5 U*1 Z until:Climb_down Z pick:0 until:opens_into Z wait:0.3 expect:rope_cut=true"

const CAVE_TO_MOTH := "D*1 R*1 D*1 R*3 D*3 R*3 D*2 R*1 until:Still_lit Z fight until:takes expect:host_done=true expect:odo_freed=false Z wait:0.3 L*1 U*2 L*3 U*3 L*3 U*1 L*1 U*1 U*1 Z until:Climb_up Z pick:0 until:Where's_my_da"

# From the dawn spawn up the north road, out of Hollowell, onto the drowned road.
const DAWN_TO_ROAD := "expect:dawn=true U*9 L*1 U*1 to:north_road settle expect:map=drowned_road"
const ROAD_FLAGS := "met_odo,odo_down,rope_cut,host_done,opened,dawn,moth_read=grief,+lantern,+poster"

const STORY := [
	{
		"name": "prologue, Odo dies, Moth is shown the lantern, the poster, the road north",
		"start": "",
		"script": HOLLOWELL_TO_CAVE + " " + CAVE_TO_MOTH + " answer:show:lantern to:his_lamp to:Was_it_yours expect:moth_read=grief answer:point:self to:I_knew_it settle " + DAWN_TO_ROAD,
	},
	{
		"name": "Odo freed: Moth's reunion, the hero points at himself, the poster, the road north",
		"start": "hollowell:well:met_odo,odo_down,rope_cut,host_done,odo_freed,odo_carried,opened",
		"script": "to:What_did_it_DO answer:point:self to:Da_says_no to:Was_it_yours expect:moth_read=truth answer:nod settle " + DAWN_TO_ROAD,
	},
	{
		"name": "drowned road: Gristle, a rotten plank, the sound boards, the Mouther, on north",
		"start": "drowned_road:south:" + ROAD_FLAGS,
		"script": "to:planks settle U*5 to:Another_one settle call:talk_gristle to:Am_I_wrong answer:shake to:eel-wine answer:shake to:left_fork answer:shake settle expect:met_gristle=true R*5 U*1 R*1 U*4 U*3 U*1 U*1 R*1 to:gives_way settle U*2 R*1 U*2 L*2 U*2 R*1 U*6 L*6 U*2 to:face_to_the_sky Z fight to:closes_over settle expect:mouther_done=true U*9 to:Tallowmouth settle expect:scene=title",
	},
	{
		"name": "drowned road: Gristle's shortcut through the leech shallows",
		"start": "drowned_road:circle:" + ROAD_FLAGS,
		"script": "wait:1 L*2 U*2 L*5 U*4 L*1 U*1 L*1 U*2 to:brushes_his_legs Z fight to:Hollowell's_wishes settle expect:leeches_done=true expect:item=pennies",
	},
	{
		"name": "blamed: the coat from a shuttered window, the road north",
		"start": "hollowell:dawn:met_odo,odo_down,rope_cut,host_done,opened,moth_read=blame,dawn",
		"script": "to:Take_it_and_go settle " + DAWN_TO_ROAD,
	},
]

const BEFORE_ROPE := "opened"
const AFTER_ROPE := "opened,met_odo,odo_down,rope_cut,met_moth"
const DEAD := "opened,met_odo,odo_down,rope_cut,met_moth,cave_seen,host_done,+lantern"
const FREED := DEAD + ",odo_freed"
const GESTURES := ["nod", "shake", "shrug", "silent"]

## Every prompt: where it starts, how to reach it, and what can be pointed at / shown there.
const PROMPTS := [
	{"name": "Odo: can you talk?", "start": "hollowell:start:" + BEFORE_ROPE,
	 "reach": "call:talk_odo to:Can_you_talk", "point": ["self", "well", "odo"]},
	{"name": "Odo: mind the rope?", "start": "hollowell:start:" + BEFORE_ROPE,
	 "reach": "call:talk_odo to:Can_you_talk answer:nod to:mind_the_rope", "point": ["self", "well", "odo"]},
	{"name": "Moth: are you drowned?", "start": "hollowell:start:" + BEFORE_ROPE,
	 "reach": "call:talk_moth to:Are_you", "point": ["self", "moth"]},
	{"name": "Moth: is he coming up?", "start": "hollowell:start:" + AFTER_ROPE,
	 "reach": "call:talk_moth to:coming_up", "point": ["self", "well", "moth"]},
	{"name": "the well: climb down?", "start": "hollowell:start:" + AFTER_ROPE,
	 "reach": "call:look_well to:Climb_down", "point": ["well"]},
	{"name": "cave: climb up?", "start": "well_cave:shaft:" + DEAD,
	 "reach": "call:climb_up to:Climb_up", "point": [], "show": ["lantern"]},
	{"name": "cave: get Odo up?", "start": "well_cave:shaft:" + FREED,
	 "reach": "call:look_odo to:Get_him_up", "point": [], "show": ["lantern"]},
	{"name": "Moth: where's my da?", "start": "hollowell:well:" + DEAD,
	 "reach": "to:Where's_my_da", "point": ["well", "self", "moth"], "show": ["lantern"]},
	{"name": "Moth: what did it do?", "start": "hollowell:well:" + FREED + ",odo_carried",
	 "reach": "to:What_did_it_DO", "point": ["well", "odo", "self", "moth"], "show": ["lantern"]},
	{"name": "dawn: was it yours?", "start": "hollowell:dawn:" + DEAD + ",moth_read=grief,dawn",
	 "reach": "to:Was_it_yours", "point": ["self", "moth"], "show": ["lantern"]},
	{"name": "Gristle: am I wrong?", "start": "drowned_road:circle:" + ROAD_FLAGS,
	 "reach": "call:talk_gristle to:Am_I_wrong", "point": ["self", "gristle"], "show": ["lantern", "poster"]},
	{"name": "Gristle: eel-wine?", "start": "drowned_road:circle:" + ROAD_FLAGS,
	 "reach": "call:talk_gristle to:Am_I_wrong answer:nod to:eel-wine", "point": ["self", "gristle"], "show": ["lantern"]},
	{"name": "Gristle: the left fork?", "start": "drowned_road:circle:" + ROAD_FLAGS,
	 "reach": "call:talk_gristle to:Am_I_wrong answer:nod to:eel-wine answer:shake to:left_fork", "point": ["self", "gristle"]},
	{"name": "salt circle: rest?", "start": "drowned_road:circle:" + ROAD_FLAGS,
	 "reach": "call:rest to:Rest_inside", "point": [], "show": ["poster"]},
	{"name": "dawn, Odo freed: was it yours?", "start": "hollowell:dawn:" + FREED + ",odo_carried,moth_read=truth,dawn",
	 "reach": "to:Was_it_yours", "point": ["self", "moth", "odo"], "show": ["lantern"]},
]

var scenarios: Array = []
var _scenario := -1
var _failed := 0


func _initialize() -> void:
	Engine.time_scale = 4.0
	var args := OS.get_cmdline_user_args()
	var which: String = args[0] if args.size() > 0 else "all"
	if which in ["all", "story"]:
		scenarios.append_array(STORY)
	if which in ["all", "sweep"]:
		for p: Dictionary in PROMPTS:
			var answers: Array = GESTURES.duplicate()
			for t: String in p["point"]:
				answers.append("point:" + t)
			for it: String in p.get("show", []):
				answers.append("show:" + it)
			for a: String in answers:
				if args.size() > 1 and not String(p["name"]).containsn(args[1]):
					continue
				scenarios.append({
					"name": "%s -> %s" % [p["name"], a],
					"start": p["start"],
					"script": "%s answer:%s settle" % [p["reach"], a],
				})
	_next()


func finished() -> bool:
	var s: Dictionary = scenarios[_scenario]
	if failures.is_empty():
		print("=== WORLD: ok   ", s["name"])
	else:
		_failed += 1
		print("=== WORLD: FAIL ", s["name"], " | ", "; ".join(failures))
	return _next()


## Starts the next scenario; returns true (quit) when none are left.
func _next() -> bool:
	if current_scene != null:
		current_scene.queue_free()
		current_scene = null
	_scenario += 1
	if _scenario >= scenarios.size():
		print("=== WORLD: %d scenarios, %d failed" % [scenarios.size(), _failed])
		quit(1 if _failed > 0 else 0)
		return true
	failures.clear()
	begin(scenarios[_scenario]["script"], scenarios[_scenario]["start"])
	return false
