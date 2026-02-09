extends Control

signal replay_pressed
signal main_menu_pressed

func _ready():
	await get_tree().create_timer(3).timeout
	get_node("Border/VBoxContainer/MainMenu").show()


func _on_main_menu_pressed() -> void:
	get_tree().change_scene_to_file("res://Scenes/scene_handler.tscn")
