extends RefCounted
## Enemy behaviours. An enemy's "ai" in scripts/data.gd names one. Each round, before anyone
## acts, decide() returns the skill the enemy will use, so it can't react to the hero's choice:
## everything it does is readable from what it did before. Add a behaviour as a function here
## plus a branch in decide().

const Battler := preload("res://scripts/battle/battler.gd")


static func decide(e: Battler) -> String:
	var ai: String = e.data.get("ai", "cycle")
	match ai:
		"cycle":
			return _cycle(e)
	push_error("enemy %s has an unknown ai: %s" % [e.id, ai])
	return _cycle(e)


# A stun (or any lost turn) breaks the rhythm: the pattern starts over.
static func lost_turn(e: Battler) -> void:
	e.ai_step = 0


# What decide() will pick next, without moving on (for whoever reads the telegraph).
static func peek(e: Battler) -> String:
	var i := _phase_now(e)
	var step := e.ai_step
	if e.data.has("phases") and i != e.phase:
		step = e.data["phases"][i].get("start", 0)
	var pattern := _pattern_of(e, i)
	return pattern[step % pattern.size()]


# The pose it stands in between moves: its phase's "rest_pose" (e.g. the whale's hide once it's
# thrown every harpoon), else normal.
static func rest_pose(e: Battler) -> String:
	if not e.data.has("phases"):
		return "normal"
	return e.data["phases"][_phase_now(e)].get("rest_pose", "normal")


# Walks its "pattern" in order, forever: lash, coil, latch, lash... An enemy with "phases" walks
# each phase's pattern until that phase's "until_used" counts are reached (skills it has used),
# then moves on to the next; it enters a phase at that phase's "start" step.
static func _cycle(e: Battler) -> String:
	var i := _phase_now(e)
	if e.data.has("phases") and i != e.phase:
		e.phase = i
		e.ai_step = e.data["phases"][i].get("start", 0)
	var pattern := _pattern_of(e, i)
	var skill: String = pattern[e.ai_step % pattern.size()]
	e.ai_step += 1
	return skill


static func _phase_now(e: Battler) -> int:
	var phases: Array = e.data.get("phases", [])
	var i := 0
	while i < phases.size() - 1 and _phase_done(e, phases[i]):
		i += 1
	return i


static func _phase_done(e: Battler, phase: Dictionary) -> bool:
	var until: Dictionary = phase.get("until_used", {})
	for s in until:
		if e.used.get(s, 0) >= until[s]:
			return true
	return false


static func _pattern_of(e: Battler, i: int) -> Array:
	if e.data.has("phases"):
		return e.data["phases"][i]["pattern"]
	return e.data["pattern"]
