extends Node2D

signal game_finished(result)
signal number_of_enemies(amount)

var map_node

var build_mode = false
var build_valid = false
var build_tile
var build_location
var build_type

var current_wave = 0
var enemies_in_wave = 0

# number of enemies spawned logged?

@onready var grace_period: Timer = $GracePeriod

func _ready():
	number_of_enemies.connect(GameData.add_enemy_amount)
	GameData.game_finished.connect(on_game_over)
	map_node = get_tree().get_first_node_in_group("maps")
	for i in get_tree().get_nodes_in_group("build_buttons"):
		i.pressed.connect(initiate_build_mode.bind(i.name))
	# not how this will be started
	# start_game event log

func get_map():
	map_node = get_tree().get_first_node_in_group("maps")

func _process(delta):
	if current_wave == (GameData.level_data[get_parent().name]["number_of_waves"] + 1) and GameData.enemy_amount == 0:
		print("waves completed")
		GameData.reset()
		get_tree().change_scene_to_file("res://Scenes/win_screen.tscn")
		
	if build_mode:
		update_tower_preview()

func start_next_wave():
	# round event log
	if current_wave <= GameData.level_data[get_parent().name]["number_of_waves"]:
		var wave_data = retrieve_wave_data()
		current_wave += 1
		spawn_enemies(wave_data)
		
	
func retrieve_wave_data():
	var wave_data = GameData.level_data[get_parent().name]["wave_" + str(current_wave)]
	var enemies_in_wave = wave_data.size()
	print("cw " + str(current_wave))
	number_of_enemies.emit(enemies_in_wave)
	return wave_data
	
func spawn_enemies(wave_data):
	map_node = get_tree().get_first_node_in_group("maps")
	for i in wave_data:
		var new_enemy = load("res://Scenes/Enemies/" + i[0] + ".tscn").instantiate()
		new_enemy.enemy_damage.connect(GameData.damage_base)
		new_enemy.enemy_death.connect(GameData.remove_enemy_amount)
		map_node.get_node("Path2D").add_child(new_enemy, true)
		await get_tree().create_timer(i[1]).timeout
	start_grace_period()

func start_grace_period():
	await get_tree().create_timer(10).timeout
	start_next_wave()

func _unhandled_input(event):
	if event.is_action_released("ui_cancel") and build_mode == true:
		cancel_build_mode()
	if event.is_action_released("ui_accept") and build_mode == true:
		verify_and_build()
		cancel_build_mode()
	
func initiate_build_mode(tower_type):
	if build_mode:
		cancel_build_mode()
	build_type = tower_type 
	build_mode = true
	get_node("UI").set_tower_preview(build_type, get_global_mouse_position())
	
func update_tower_preview():
	map_node = get_tree().get_first_node_in_group("maps")
	var mouse_position = get_global_mouse_position()
	var tilemap: TileMapLayer = map_node.get_node("Ground/TowerExclusion")
	var layer := 0


	var local_pos = tilemap.to_local(mouse_position)
	var current_tile = tilemap.local_to_map(local_pos)

	var tile_position = tilemap.to_global(
		tilemap.map_to_local(current_tile)
	)

	if tilemap.get_cell_source_id(current_tile) == -1:
		$UI.update_tower_preview(tile_position, "c7c7c7")
		build_valid = true
		build_location = tile_position
		build_tile =  current_tile
	else:
		$UI.update_tower_preview(tile_position, "c91748")
		build_valid = false

	
func cancel_build_mode():
	build_mode = false
	build_valid = false
	get_node("UI/TowerPreview").free()
	
func verify_and_build():
	var cost = GameData.tower_data[build_type]["cost"]
	if build_valid and GameData.spend(cost):
		var new_tower = load("res://Scenes/Towers/" + build_type + ".tscn").instantiate()
		new_tower.position = build_location
		new_tower.built = true
		map_node.get_node("Towers").add_child(new_tower, true)
		map_node.get_node("Ground/TowerExclusion").set_cell(build_tile, 3, Vector2i(0, 0))
		#deduct cash
		#update cash ui

func on_game_over(result):
	if result == "lose":
		GameData.reset()
		get_tree().change_scene_to_file("res://Scenes/game_over.tscn")
	elif result == "win":
		GameData.reset()
		get_tree().change_scene_to_file("res://Scenes/win_screen.tscn")

#func on_damage(damage):
#	base_health -= damage
#	if base_health <= 0:
#		emit_signal("game_finished", false)
#	else:
#		get_node("UI").update_health_bar(base_health)
