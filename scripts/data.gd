extends RefCounted
## Game data tables. Add enemies and items here; the battle code reads from these.

const HERO := {
	"name": "Wanderer",  # placeholder -- rename freely
	"max_hp": 60,
	"max_mp": 10,        # unused so far; Drained eats it, skills will spend it
	"atk": 10,
	"agi": 10,
}

const ITEMS := {
	"salve": {"name": "Salve", "heal": 15, "cures_drained": true, "start": 2},
}

const ENEMIES := {
	"sucker_frog": {
		"name": "Sucker Frog",
		"max_hp": 80,
		"def": 0,
		"agi": 6,
		# Scripted cycle: hit, telegraph, big move. Guarding on the turn after the coil
		# turns the Latch into a stun -- that's the tutorial's lesson.
		"pattern": ["lash", "coil", "latch"],
	},
}

# Tutorial mercy: damage can never take the hero below 1 HP.
const MERCY := true
