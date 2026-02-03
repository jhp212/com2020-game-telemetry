extends Node

func _ready():
	# Connect Main Menu buttons
	get_node("MainMenu/Border/VBoxContainer/PlayButton").pressed.connect(Callable(self, "on_play_pressed"))
	get_node("MainMenu/Border/VBoxContainer/LevelsButton").pressed.connect(Callable(self, "on_levels_pressed"))
	
	# Connect Level Selection buttons
	get_node("LevelSelection/Border/VBoxContainer/Row1/Level1").pressed.connect(Callable(self, "on_levels_1_pressed"))
	get_node("LevelSelection/Border/VBoxContainer/Row1/Level2").pressed.connect(Callable(self, "on_levels_2_pressed"))
	get_node("LevelSelection/Border/VBoxContainer/BackButton").pressed.connect(Callable(self, "on_back_button_pressed"))

func on_play_pressed():
	get_node("MainMenu").queue_free()
	# change loaded scene to continue in future?
	var current_level = load("res://Scenes/Levels/level_1.tscn").instantiate()
	add_child(current_level)
	
func on_levels_pressed():
	get_node("LevelSelection").show()

func on_back_button_pressed():
	get_node("LevelSelection").hide()

func on_levels_1_pressed():
	get_node("MainMenu").queue_free()
	get_node("LevelSelection").queue_free()
	var current_level = load("res://Scenes/Levels/level_1.tscn").instantiate()
	add_child(current_level)

func on_levels_2_pressed():
	get_node("MainMenu").queue_free()
	get_node("LevelSelection").queue_free()
	var current_level = load("res://Scenes/Levels/level_2.tscn").instantiate()
	add_child(current_level)
