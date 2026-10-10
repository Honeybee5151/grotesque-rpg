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


# Walks its "pattern" in order, forever: lash, coil, latch, lash...
static func _cycle(e: Battler) -> String:
	var pattern: Array = e.data["pattern"]
	var skill: String = pattern[e.ai_step % pattern.size()]
	e.ai_step += 1
	return skill
