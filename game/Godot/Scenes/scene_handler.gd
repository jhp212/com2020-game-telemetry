extends Node

func _ready():
	# Connect Main Menu buttons
	get_node("MainMenu/Border/VBoxContainer/PlayButton").pressed.connect(Callable(self, "on_play_pressed"))
	get_node("MainMenu/Border/VBoxContainer/LevelsButton").pressed.connect(Callable(self, "on_levels_pressed"))
	
	# Connect Level Selection buttons
	get_node("LevelSelection/Border/VBoxContainer/Row1/Level1").pressed.connect(Callable(self, "on_levels_1_pressed"))
	get_node("LevelSelection/Border/VBoxContainer/Row1/Level2").pressed.connect(Callable(self, "on_levels_2_pressed"))
	get_node("LevelSelection/Border/VBoxContainer/Row1/Level3").pressed.connect(Callable(self, "on_levels_3_pressed"))
	get_node("LevelSelection/Border/VBoxContainer/Row1/Level4").pressed.connect(Callable(self, "on_levels_4_pressed"))
	get_node("LevelSelection/Border/VBoxContainer/Row1/Level5").pressed.connect(Callable(self, "on_levels_5_pressed"))
	get_node("LevelSelection/Border/VBoxContainer/Row2/Level6").pressed.connect(Callable(self, "on_levels_6_pressed"))
	get_node("LevelSelection/Border/VBoxContainer/Row2/Level7").pressed.connect(Callable(self, "on_levels_7_pressed"))
	get_node("LevelSelection/Border/VBoxContainer/Row2/Level8").pressed.connect(Callable(self, "on_levels_8_pressed"))
	get_node("LevelSelection/Border/VBoxContainer/Row2/Level9").pressed.connect(Callable(self, "on_levels_9_pressed"))
	get_node("LevelSelection/Border/VBoxContainer/Row2/Level10").pressed.connect(Callable(self, "on_levels_10_pressed"))
	get_node("LevelSelection/Border/VBoxContainer/BackButton").pressed.connect(Callable(self, "on_back_button_pressed"))
	

func on_play_pressed():
	# Changes scene to Level1
	GameData.current_stage = 1
	get_tree().change_scene_to_file("res://Scenes/Levels/level_1.tscn")

func on_levels_pressed():
	# Go to LevelSelection page
	get_node("LevelSelection").show()

func on_back_button_pressed():
	# Go back to main menu
	get_node("LevelSelection").hide()

func on_levels_1_pressed():
	# Changes scene to Level1
	GameData.current_stage = 1
	get_tree().change_scene_to_file("res://Scenes/Levels/level_1.tscn")

func on_levels_2_pressed():
	# Changes scene to Level2
	GameData.current_stage = 2
	get_tree().change_scene_to_file("res://Scenes/Levels/level_2.tscn")

func on_levels_3_pressed():
	# Changes scene to Level2
	GameData.current_stage = 3
	get_tree().change_scene_to_file("res://Scenes/Levels/level_3.tscn")

func on_levels_4_pressed():
	# Changes scene to Level2
	GameData.current_stage = 4
	get_tree().change_scene_to_file("res://Scenes/Levels/level_4.tscn")

func on_levels_5_pressed():
	# Changes scene to Level1
	GameData.current_stage = 1
	get_tree().change_scene_to_file("res://Scenes/Levels/level_5.tscn")

func on_levels_6_pressed():
	# Changes scene to Level2
	GameData.current_stage = 2
	get_tree().change_scene_to_file("res://Scenes/Levels/level_6.tscn")

func on_levels_7_pressed():
	# Changes scene to Level2
	GameData.current_stage = 3
	get_tree().change_scene_to_file("res://Scenes/Levels/level_7.tscn")
	
func on_levels_8_pressed():
	# Changes scene to Level2
	GameData.current_stage = 4
	get_tree().change_scene_to_file("res://Scenes/Levels/level_8.tscn")

func on_levels_9_pressed():
	# Changes scene to Level2
	GameData.current_stage = 3
	get_tree().change_scene_to_file("res://Scenes/Levels/level_9.tscn")
	
func on_levels_10_pressed():
	# Changes scene to Level2
	GameData.current_stage = 4
	get_tree().change_scene_to_file("res://Scenes/Levels/level_10.tscn")

#func on_game_over(result):
#	if result == "lose":
#
#		var game_over_scene = load("res://Scenes/game_over.tscn").instantiate()
#		add_child(game_over_scene)
#		game_over_scene.replay_pressed.connect(replay_level_pressed)
#		game_over_scene.main_menu_pressed.connect(main_menu_pressed)
#		await get_tree().create_timer(2.9).timeout
#		get_node("Level1").queue_free()
