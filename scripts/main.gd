extends Node2D
## The tutorial fight on its own, where the title screen's Play lands: the hero against the Host,
## then Z fights again and X goes back to the title. The battle itself is scripts/battle/battle.gd,
## which the world starts the same way.

const Battle := preload("res://scripts/battle/battle.gd")


func _ready() -> void:
	RenderingServer.set_default_clear_color(Color("#07050d"))
	while true:
		var battle := Battle.new()
		add_child(battle)
		await battle.run(["host"])
		await battle.view.say("Z: fight again    X: title screen", 0.0)
		var again: bool = await battle.view.wait_choice()
		battle.queue_free()
		if not again:
			get_tree().change_scene_to_file("res://title.tscn")
			return
