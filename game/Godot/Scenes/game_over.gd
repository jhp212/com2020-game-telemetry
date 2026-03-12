extends Control

# Signals for when buttons are pressed
signal replay_pressed
signal main_menu_pressed



func _ready():
	# Wait 3 seconds before buttons are visible
	await get_tree().create_timer(3).timeout
	get_node("Border/VBoxContainer/ReplayLevel").show()
	get_node("Border/VBoxContainer/MainMenu").show()

func _on_replay_level_pressed() -> void:
	# Replay level
	get_tree().change_scene_to_file("res://Scenes/Levels/level_" + str(GameData.current_stage) + ".tscn")

func _on_main_menu_pressed() -> void:
	# Back to main menu
	
	get_tree().change_scene_to_file("res://Scenes/scene_handler.tscn")
