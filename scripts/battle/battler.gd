extends RefCounted
## One combatant, the hero or an enemy: its numbers and states. Stats come from scripts/data.gd.

const Data := preload("res://scripts/data.gd")

var id: String           # "hero" or the enemy's id in Data.ENEMIES
var name: String         # as it reads mid-sentence: "the Host"
var is_hero := false
var data: Dictionary     # the enemy's row in Data.ENEMIES (empty for the hero)
var max_hp: int
var max_mp: int
var hp: int
var mp: int
var atk: int
var def: int
var agi: int
var skills: Array = []       # skill ids the hero can choose from (enemies use their pattern)
var states: Dictionary = {}  # state id -> stacks
var guarding := false        # until the start of the next round
var telegraphing := false    # its last move was a warning; the big one comes next
var lost_turn := false       # a skip_turn state ate its action this round
var ai_step := 0             # where an enemy is in its pattern (scripts/battle/enemy_ai.gd)
var gone := false            # died and has been cleared away


# carry: {hp, mp, states, skills} brought in from outside the battle; missing keys mean fresh.
func setup_hero(carry: Dictionary = {}) -> RefCounted:
	var h: Dictionary = Data.HERO
	id = "hero"
	name = h["name"]
	is_hero = true
	max_hp = h["max_hp"]
	max_mp = h["max_mp"]
	hp = carry.get("hp", max_hp)
	mp = carry.get("mp", max_mp)
	atk = h["atk"]
	def = h.get("def", 0)
	agi = h["agi"]
	states = Dictionary(carry.get("states", {})).duplicate()
	skills = Array(carry.get("skills", h.get("skills", []))).duplicate()
	return self


func setup_enemy(enemy_id: String) -> RefCounted:
	data = Data.ENEMIES[enemy_id]
	id = enemy_id
	name = data["name"]
	max_hp = data["max_hp"]
	max_mp = data.get("max_mp", 0)
	hp = max_hp
	mp = max_mp
	atk = data.get("atk", 0)
	def = data.get("def", 0)
	agi = data["agi"]
	return self


func alive() -> bool:
	return hp > 0


func stacks(state: String) -> int:
	return states.get(state, 0)


func skips_turn() -> bool:
	for s in states:
		if Data.STATES[s].get("skip_turn", false):
			return true
	return false


# Attack after states: Drained takes 10% per stack.
func atk_mult() -> float:
	var m := 1.0
	for s in states:
		m += float(Data.STATES[s].get("atk_per_stack", 0.0)) * states[s]
	return m
