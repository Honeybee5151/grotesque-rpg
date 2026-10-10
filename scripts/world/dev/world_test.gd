extends "res://scripts/world/dev/drive.gd"
## Headless playthroughs of the prologue, for the merge checks:
##   godot --headless --path . --script res://scripts/world/dev/world_test.gd
## Each scenario is a key script for drive.gd plus the flags it must leave behind. Prints one
## "=== WORLD:" line per scenario and exits 1 if any step timed out or any expectation missed.

const HOLLOWELL_TO_CAVE := "until:They_pulled Z until:coughed Z wait:1.4 R*4 U*5 until:drowned_man_walks Z until:look_at_you Z U*1 wait:0.2 U*1 wait:0.2 L*1 Z until:sleep_till Z until:keeps_me Z until:Can_you_talk Z pick:0 until:Go_on Z until:liar Z until:parish Z until:pennies Z until:penny Z until:spawn. Z until:going_down Z until:mind_the_rope Z pick:4 until:law Z until:Moth! Z until:Two_tugs! Z until:hauls Z until:bitten Z until:Da? Z wait:0.5 U*1 Z until:Climb_down Z pick:0 until:opens_into Z wait:0.3 expect:rope_cut=true"

const CAVE_TO_MOTH := "D*1 R*1 D*1 R*3 D*3 R*3 D*2 R*1 until:Still_lit Z fight expect:host_done=true expect:odo_freed=false R*1 Z until:takes Z wait:0.3 L*2 U*2 L*3 U*3 L*3 U*1 L*1 U*1 U*1 Z until:Climb_up Z pick:0 until:Where's_my_da"

const SCENARIOS := [
	{
		"name": "prologue, Odo dies, Moth is shown the lantern",
		"start": "",
		"script": HOLLOWELL_TO_CAVE + " " + CAVE_TO_MOTH + " Z pick:4 wait:0.1 Z until:his_lamp Z until:Not_to_sleep Z until:Oh Z until:keeps_it_lit Z until:end_of_the_beginning expect:moth_read=grief Z until:Thanks Z wait:1.5 expect:scene=title",
	},
	{
		"name": "Odo freed: Moth's reunion, the hero points at himself",
		"start": "hollowell:well:met_odo,odo_down,rope_cut,host_done,odo_freed,odo_carried,opened",
		"script": "until:DA! Z until:your_head Z until:Say_something Z until:What_did_it_DO Z pick:3 wait:0.1 pick:2 until:You_did_this Z until:Da_says_no Z until:doesn't_need Z until:understand Z until:end_of_the_beginning expect:moth_read=truth Z until:Thanks Z wait:1.5 expect:scene=title",
	},
]

var _scenario := -1
var _failed := 0


func _initialize() -> void:
	Engine.time_scale = 2.0
	_next()


func finished() -> bool:
	var s: Dictionary = SCENARIOS[_scenario]
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
	if _scenario >= SCENARIOS.size():
		print("=== WORLD: %d scenarios, %d failed" % [SCENARIOS.size(), _failed])
		quit(1 if _failed > 0 else 0)
		return true
	failures.clear()
	begin(SCENARIOS[_scenario]["script"], SCENARIOS[_scenario]["start"])
	return false
