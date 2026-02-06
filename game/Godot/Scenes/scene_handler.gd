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
	# change loaded scene to continue in future?
	get_tree().change_scene_to_file("res://Scenes/Levels/level_1.tscn")

func on_levels_pressed():
	get_node("LevelSelection").show()

func on_back_button_pressed():
	get_node("LevelSelection").hide()

func on_levels_1_pressed():
	get_tree().change_scene_to_file("res://Scenes/Levels/level_1.tscn")

func on_levels_2_pressed():
	get_tree().change_scene_to_file("res://Scenes/Levels/level_2.tscn")

#func on_game_over(result):
#	if result == "lose":
#
#		var game_over_scene = load("res://Scenes/game_over.tscn").instantiate()
#		add_child(game_over_scene)
#		game_over_scene.replay_pressed.connect(replay_level_pressed)
#		game_over_scene.main_menu_pressed.connect(main_menu_pressed)
#		await get_tree().create_timer(2.9).timeout
#		get_node("Level1").queue_free()
