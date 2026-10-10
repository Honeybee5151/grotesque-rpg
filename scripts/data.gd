extends RefCounted
## Game data tables. The battle (scripts/battle/) takes every number and line of battle text from
## here: new enemies, skills, states and items are data, not code. The rules: docs/combat.md.
##
## Battle text: a line is a String, or a Dictionary {"say": text, "hold": seconds, "sfx": sound,
## "pose": pose, "flash": colour, "shake": true, "pop": text}. Its cues fire as the line starts;
## pose/flash/shake act on the enemy using the skill (or holding the state), pop is a speech
## bubble over the hero. Placeholders: {hero}, {user}, {target}, {name} (the state's holder),
## written as names appear mid-sentence ("the Host"); {User}, {Target}, {Name} capitalise the
## first letter. Numbers: {dmg}, {heal}, {hp}, {mp}, {stacks}. A filled line must fit the log
## window: 214px of the Grotesk pixel font, about 42 characters (say() warns when it doesn't).

const HERO := {
	"name": "Wanderer",  # placeholder -- rename freely
	"max_hp": 60,
	"max_mp": 10,        # skills spend it, Drained eats it
	"atk": 10,
	"def": 0,
	"agi": 10,
	"skills": ["crush", "mend"],  # a caller can bring its own list (context.hero.skills)
}

const RULES := {
	"variance": 0.15,     # attack-based hits roll x(1 - variance .. 1 + variance); a skill can set its own
	"crit_chance": 0.1,   # for skills with "crit": true
	"crit_mult": 1.5,
	"guard_mult": 0.5,    # a guarded hit deals this much, rounded up
	"min_damage": 1,
}

# Skills. Damage is either "power" (x the user's attack, rolled, minus the target's defence) or
# "dmg": [min, max] (flat roll, minus defence). "heal" restores HP. "mp" is the cost. "target":
# "self" for moves on yourself (the default is one enemy; enemies always aim at the hero).
# "priority" acts before everyone else.
# "telegraph" marks the warning move before a big one. "guard_blocks": a guarding target takes
# nothing, says the "blocked" lines and puts "blocked_user_states" on the user.
const SKILLS := {
	# --- the hero ---
	"attack": {
		"name": "Attack",
		"power": 1.0,
		"crit": true,
		"hit": "{user} strikes! {Target} takes {dmg}.",
		"crit_hit": "A clean hit! {Target} takes {dmg}.",
	},
	"guard": {
		"name": "Guard",
		"target": "self",
		"guard": true,
		"priority": 1,
		"lines": [{"say": "{user} braces himself.", "sfx": "guard"}],
	},
	# The mute hero's skills are things he does, not words he says. Crush is the punish:
	# x2, and x4 on a stunned enemy, so it's worth saving for the stun. A sure blow: no roll, no crit.
	"crush": {
		"name": "Crush",
		"mp": 4,
		"power": 2.0,
		"variance": 0.0,
		"lines": [{"say": "{user} throws his whole weight into it!", "hold": 0.35}],
		"hit": "{Target} takes {dmg}.",
	},
	"mend": {
		"name": "Mend",
		"mp": 3,
		"target": "self",
		"heal": 16,
		"lines": [{"say": "{user} presses a hand to his wounds.", "sfx": "heal"}],
	},
	# --- the Host: lash -> coil (telegraph) -> latch ---
	"lash": {
		"lines": ["A tongue lashes out of {user}'s mouth!"],
		"dmg": [5, 8],
		"hit": "{Target} takes {dmg} damage.",
	},
	"coil": {
		"telegraph": true,
		"lines": [
			{"say": "{User}'s head tips back, jaw unhinged.", "hold": 0.35,
				"pose": "telegraph", "flash": "#ffb0c8", "sfx": "coil"},
			"The sucker flexes on its brain, hungry.",
		],
	},
	"latch": {
		"lines": [{"say": "The sucker lunges for {target}'s head!", "hold": 0.5}],
		"dmg": [4, 6],
		"states": {"drained": 1},
		"hit": "It clamps on! He takes {dmg} damage.",
		"guard_blocks": true,
		"blocked": [{"say": "It slaps his raised arms and slips off!", "sfx": "guard", "shake": true}],
		"blocked_user_states": {"stunned": 1},
	},
}

# States: id -> stacks on a battler. "skip_turn" states eat the holder's next action and wear off
# at the end of that round. "damage_taken" multiplies every hit on the holder, and its "hit" line
# replaces the skill's own. "tick_hp"/"tick_mp" are lost per stack at the end of every round.
# "atk_per_stack" changes attack (x(1 + n * value)). "ends_with_battle" states don't carry over.
# An enemy can say any of a state's lines its own way ("state_text" in ENEMIES).
const STATES := {
	"drained": {
		"label": "DRAINED x{stacks}",
		"max_stacks": 3,
		"atk_per_stack": -0.1,
		"tick_hp": 3,
		"tick_mp": 1,
		"apply": [{"say": "Drained x{stacks}! Something warm slips away.", "sfx": "drain"}],
		"tick": [{"say": "Drained... -{hp} HP, -{mp} MP.", "hold": 0.5, "sfx": "drain"}],
		"cure": "The drain lifts.",
		"ends_with_battle": true,
	},
	"stunned": {
		"label": "STUNNED",
		"skip_turn": true,
		"damage_taken": 2.0,  # answering a telegraph pays off in speed, not just HP
		"apply": ["{Name} reels, stunned."],
		"hit": "{Target} is wide open! It takes {dmg}.",
		"skip": ["{Name} is still reeling."],
		"ends_with_battle": true,
	},
}

const ITEMS := {
	"salve": {
		"name": "Salve",
		"heal": 15,
		"cures": ["drained"],
		"start": 2,
		"lines": [{"say": "{user} smears on a Salve.", "sfx": "heal"}],
	},
}

# Enemies. "name" is written as it reads mid-sentence. "sprite" picks art/monsters/<sprite>/
# (normal.png, telegraph.png, stunned.png, hurt.png). "ai" picks a behaviour in
# scripts/battle/enemy_ai.gd. "intro" opens the fight unless the caller brings its own,
# "death" is said when it falls; "death_when": {state: {flag, lines}} replaces it when it falls
# holding that state, and puts the flag in the battle's result. "mercy": the hero can't drop below
# 1 HP in a fight with it. "state_text": {state: {key: lines}} says a state's lines its own way.
const ENEMIES := {
	"host": {
		"name": "the Host",
		"sprite": "host",
		# 58 = two attacks (at least 9 each) + a Crush on the stun (exactly 40): read the first coil,
		# Crush the stun, and the man is freed. Miss the first read and there's a second cycle.
		"max_hp": 58,
		"atk": 0,
		"def": 0,
		"agi": 6,
		# Scripted cycle: hit, telegraph, big move. Guarding on the turn after the coil
		# turns the Latch into a stun -- that's the tutorial's lesson.
		"ai": "cycle",
		"pattern": ["lash", "coil", "latch"],
		"mercy": true,  # tutorial
		"intro": [
			"A man staggers out of the dark.",
			"Something wet rides his shoulders.",
			{"say": "{hero} says nothing. He nods, once.", "pop": "..."},
		],
		# The guarded latch tears the sucker out: the frog hangs dazed, the man is himself again.
		"state_text": {
			"stunned": {
				"apply": ["{Name} reels, stunned.", "For a moment, the man's eyes clear."],
				"hit": "The frog's belly is bare! It takes {dmg}.",
				"skip": ["The frog crawls back onto his skull."],
			},
		},
		"death": ["The frog peels away, spent. The man falls.", "He was already gone."],
		# Killed while stunned, its sucker torn out of his skull: the man lives (world: Odo).
		"death_when": {
			"stunned": {
				"flag": "freed",
				"lines": ["The frog peels away, spent. The man falls.", "He's still breathing."],
			},
		},
	},
}

# Lines the battle itself says.
const TEXT := {
	"heal": "{heal} HP restored.",
	"guarded": " (guarded)",
	"victory": ["Victory."],
	"defeat": ["{hero} collapses.", "Everything goes quiet."],
	"flee": ["{hero} backs away into the dark."],
	"no_mp": ["{User} tries, but he's spent."],
}
