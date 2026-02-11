extends Control

# Signals for when the buttons are pressed
signal replay_pressed
signal main_menu_pressed

func _ready():
	# Wait 3 seconds before the buttons are visible
	await get_tree().create_timer(3).timeout
	get_node("Border/VBoxContainer/MainMenu").show()

func _on_main_menu_pressed() -> void:
	# Go to main menu
	get_tree().change_scene_to_file("res://Scenes/scene_handler.tscn")
