extends Node2D


var map_node

var build_mode = false
var build_valid = false
var build_tile
var build_location
var build_type

var current_wave = 0
var enemies_in_wave = 0
# number of enemies spawned logged?

func _ready():
	map_node = get_node("Level1Map")
	
	for i in get_tree().get_nodes_in_group("build_buttons"):
		i.pressed.connect(initiate_build_mode.bind(i.name))
	# not how this will be started
	# start_game event log
	start_next_wave()


func _process(delta):
	if build_mode:
		update_tower_preview()

func start_next_wave():
	# round event log
	var wave_data = retrieve_wave_data()
	await get_tree().create_timer(0.2).timeout
	spawn_enemies(wave_data)
	
func retrieve_wave_data():
	var wave_data = [["medium_circle", 2], ["medium_circle", 2], ["large_circle", 2], ["small_circle", 0.5], ["small_circle", 0.5], ["small_circle", 0.5]]
	current_wave += 1
	enemies_in_wave = wave_data.size()
	return wave_data
	
func spawn_enemies(wave_data):
	for i in wave_data:
		var new_enemy = load("res://Scenes/Enemies/" + i[0] + ".tscn").instantiate()
		map_node.get_node("Path2D").add_child(new_enemy, true)
		await get_tree().create_timer(i[1]).timeout

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
	var mouse_position = get_global_mouse_position()
	var tilemap: TileMap = map_node.get_node("TowerExclusion")
	var layer := 0


	var local_pos = tilemap.to_local(mouse_position)
	var current_tile = tilemap.local_to_map(local_pos)

	var tile_position = tilemap.to_global(
		tilemap.map_to_local(current_tile)
	)

	if tilemap.get_cell_source_id(layer, current_tile) == -1:
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
	if build_valid:
		#check cash
		var new_tower = load("res://Scenes/Towers/" + build_type + ".tscn").instantiate()
		new_tower.position = build_location
		new_tower.built = true
		map_node.get_node("Towers").add_child(new_tower, true)
		map_node.get_node("TowerExclusion").set_cell(-1, build_tile, 3, Vector2i(0, 0))
		#deduct cash
		#update cash ui
