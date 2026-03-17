extends Node2D

# Signal for game state changes
signal game_finished(result)
signal number_of_enemies(amount)

# Connect nodes
@export var level: int
@onready var grace_period: Timer = $GracePeriod
@onready var upgrade_1: Button = $UI/TowerPanel/VBoxContainer/HBoxContainer/Panel/MarginContainer/VBoxContainer/HBoxContainer/Upgrade1

# Map reference
var map_node

# Build
var build_mode = false
var build_valid = false
var build_tile
var build_location
var build_type

# Tracking waves
var current_wave = 0
var enemies_in_wave = 0

var selected_tower

func _ready():
	$UI/TowerPanel.sell.connect(sell_tower)
	# Connect signals for enemy count and game over
	number_of_enemies.connect(GameData.add_enemy_amount)
	GameData.game_finished.connect(on_game_over)
	# Get map
	map_node = get_tree().get_first_node_in_group("maps")
	# Connect build buttons
	for i in get_tree().get_nodes_in_group("build_buttons"):
		i.pressed.connect(initiate_build_mode.bind(i.name))
	# Set current stage and log telemetry event
	#GameData.current_stage = level
	#Telemetry.log_event("stage_start", {})

func get_map():
	# Refresh map reference
	map_node = get_tree().get_first_node_in_group("maps")

func _process(delta):
	# Check for win condition and log telemetry event
	if current_wave == (GameData.level_data[get_parent().name]["number_of_waves"] + 1) and GameData.enemy_amount == 0:
		Telemetry.log_event("stage_end", {})
		GameData.reset()
		get_tree().change_scene_to_file("res://Scenes/win_screen.tscn")
	if current_wave == (GameData.level_data[get_parent().name]["number_of_waves"] + 1) and GameData.enemy_amount < 0:
		print("Number of enemies is less than one, this is invalid!")
	# Update toqer preview when placing
	if build_mode:
		update_tower_preview()

func start_next_wave():
	# Start next wave
	update_wave_counter()
	## round event log
	if current_wave <= GameData.level_data[get_parent().name]["number_of_waves"]:
		var wave_data = retrieve_wave_data()
		if current_wave != 1:
			GameData.add_money(300 + (20 * (current_wave - 1)))
		current_wave += 1
		spawn_enemies(wave_data)

func retrieve_wave_data():
	# Get wave data from GameData
	var wave_data = GameData.level_data[get_parent().name]["wave_" + str(current_wave)]
	var enemies_in_wave = wave_data.size()
	# Notify GameData how many enemies will spawn
	number_of_enemies.emit(enemies_in_wave)
	return wave_data

func spawn_enemies(wave_data):
	# Spawn enemies one by one with predetermined delays
	map_node = get_tree().get_first_node_in_group("maps")
	for i in wave_data:
		var new_enemy = load("res://Scenes/Enemies/" + i[0] + ".tscn").instantiate()
		# Connect enemy signals
		new_enemy.enemy_damage.connect(GameData.damage_base)
		new_enemy.enemy_death.connect(GameData.remove_enemy_amount)
		map_node.get_node("Path2D").add_child(new_enemy, true)
		$WaveTimer.wait_time = i[1]
		$WaveTimer.start()
		await $WaveTimer.timeout
	start_grace_period()

var grace_time := 20
var grace_running := false
var skip_requested := false


func start_grace_period():
	grace_running = true
	$UI/HUD/WaveTracker/SkipButton.show()
	$UI/HUD/WaveTracker/GraceTimerLabel.show()
	var time_left = grace_time
	while time_left > 0 and grace_running:
		$UI/HUD/WaveTracker/GraceTimerLabel.text = "Next wave in: %d" % time_left
		$GraceTimer.start()
		await $GraceTimer.timeout
		if skip_requested:
			skip_requested = false
			break
		time_left -= 1
	grace_running = false
	$UI/HUD/WaveTracker/GraceTimerLabel.hide()
	$UI/HUD/WaveTracker/SkipButton.hide()
	start_next_wave()

func _on_skip_button_pressed() -> void:
	skip_requested = true
	grace_running = false


func _unhandled_input(event):
	# Cancel build mode
	if event.is_action_released("ui_cancel") and build_mode == true:
		cancel_build_mode()
	# Confirm tower placement
	if event.is_action_released("ui_accept") and build_mode == true:
		verify_and_build()
		cancel_build_mode()

func initiate_build_mode(tower_type):
	# Start building a tower
	if build_mode:
		cancel_build_mode()
	build_type = tower_type 
	build_mode = true
	# Create preview at position of mouse
	get_node("UI").set_tower_preview(build_type, get_global_mouse_position())

func update_tower_preview():
	# Update preview position and color based on tile validity
	map_node = get_tree().get_first_node_in_group("maps")
	var mouse_position = get_global_mouse_position()
	var tilemap: TileMapLayer = map_node.get_node("Ground/TowerExclusion")
	var layer := 0


	var local_pos = tilemap.to_local(mouse_position)
	var current_tile = tilemap.local_to_map(local_pos)

	var tile_position = tilemap.to_global(
		tilemap.map_to_local(current_tile)
	)
	# Check if tile is valid
	if tilemap.get_cell_source_id(current_tile) == -1:
		$UI.update_tower_preview(tile_position, "c7c7c7")
		build_valid = true
		build_location = tile_position
		build_tile =  current_tile
	else:
		$UI.update_tower_preview(tile_position, "c91748")
		build_valid = false

	
func cancel_build_mode():
	# Remove preview
	build_mode = false
	build_valid = false
	get_node("UI/TowerPreview").free()
	
func verify_and_build():
	# Cost of selected tower
	var cost = GameData.tower_data[build_type]["cost"]
	# Only build if placement is valid and player has enough money
	if build_valid and GameData.spend(cost):
		# Create tower
		var new_tower = load("res://Scenes/Towers/" + build_type + ".tscn").instantiate()
		new_tower.tower_clicked.connect(on_tower_clicked)
		new_tower.position = build_location
		new_tower.built = true
		map_node.get_node("Towers").add_child(new_tower, true)
		# Mark tile as occupied
		map_node.get_node("Ground/TowerExclusion").set_cell(build_tile, 3, Vector2i(0, 0))
		#update cash ui

func on_game_over(result):
	# Handle losing and log telemetry event
	if result == "lose":
		Telemetry.log_event("stage_fail", {})
		GameData.reset()
		get_tree().change_scene_to_file("res://Scenes/game_over.tscn")
	# Handle wining and log telemetry event
	#elif result == "win":
	#	Telemetry.log_event("stage_end", {})
	#	GameData.reset()
	#	get_tree().change_scene_to_file("res://Scenes/win_screen.tscn")


func on_tower_clicked(tower):
	selected_tower = tower
	if $UI/TowerPanel.shown == false:
		$UI/AnimationPlayer.play("tower_panel_up")
		$UI/TowerPanel.shown = true
	$UI/TowerPanel.set_tower(tower)

	# Connect the panel's upgrade signal to a handler
	$UI/TowerPanel.upgrade.connect(request_upgrade)

func request_upgrade(tower):
	var upgrade_cost = GameData.tower_upgrades[tower.tower_type]["1cost"]
	if GameData.spend(upgrade_cost):
		
		var new_tower = tower.upgrade(tower)
	
		new_tower.tower_clicked.connect(on_tower_clicked)
		
		on_tower_clicked(new_tower)

func sell_tower(tower):
	var money_back = GameData.tower_upgrades[tower.tower_type]["sell_price"]
	GameData.add_money(money_back)
	tower.sold()

func update_wave_counter():
	$UI/HUD/WaveTracker/WaveCounter.text = str(current_wave)
