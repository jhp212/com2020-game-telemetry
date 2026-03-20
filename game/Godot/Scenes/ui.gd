extends CanvasLayer

# Connect nodes
@onready var health_bar: TextureProgressBar = $HUD/HealthUI/HBoxContainer/HealthBar
@onready var cash: Label = $HUD/CashUI/HBoxContainer/Cash
@onready var triangle_cost: Label = $HUD/TowerBuildPanel/HBoxContainer/BuildBar/Margin/TowerList/Panel/Triangle/TriangleCost
@onready var square_cost: Label = $HUD/TowerBuildPanel/HBoxContainer/BuildBar/Margin/TowerList/Panel2/Square/SquareCost
@onready var star_cost: Label = $HUD/TowerBuildPanel/HBoxContainer/BuildBar/Margin/TowerList/Panel3/Star/StarCost
@onready var volume_slider = $HUD/PauseMenu/VolumeSlider
@onready var volume_value_label = $HUD/PauseMenu/VolumeValueLabel

var current_tween: Tween
var lose

var selected_tower

var tower_build_panel_shown = false

# Signal for when the game ends
signal game_finished(result)

func _ready():
	# Show HUD and connect to GameData signals
	self.show()
	GameData.base_health_changed.connect(update_health_bar)
	update_health_bar(GameData.base_health)
	GameData.money_changed.connect(update_money)
	update_money(GameData.money)
	# Play "pulse" animation on the play/pause button
	$HUD/PausePlay/AnimationPlayer.play("pulse")
	
	triangle_cost.text = str("$" + str(GameData.tower_data["triangle_stock"]["cost"]))
	square_cost.text = str("$" + str(GameData.tower_data["square_stock"]["cost"]))
	star_cost.text = str("$" + str(GameData.tower_data["star_stock"]["cost"]))
	
	var volume := AudioServer.get_bus_volume_linear(AudioServer.get_bus_index("Master"))
	volume_slider.value = volume
	volume_value_label.text = str(int(volume*100))
	
	volume_slider.connect("value_changed", _on_slider_moved)
	volume_slider.connect("drag_ended", _on_drag_ended)

func _on_slider_moved(value: float):
	volume_value_label.text = "{0}%".format([int(value*100)])

func _on_drag_ended(moved: bool):
	if moved:
		AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Master"), linear_to_db(volume_slider.value))
		$HUD/PauseMenu/PlacementSfx.play()
		
func update_money(amount: int):
	# Update displayed cash
	cash.text = str("$" + str(amount))

func set_tower_preview(tower_type, mouse_position):
	# create a preview of the tower being placed
	var drag_tower = load("res://Scenes/Towers/" + tower_type + ".tscn").instantiate()
	drag_tower.set_name("DragTower")
	drag_tower.modulate = Color("8a8a8a")
	
	# Create range indicator
	var range_texture = Sprite2D.new()
	range_texture.position = Vector2(0,0)
	var scaling = GameData.tower_data[tower_type]["range"] / 600.0
	range_texture.scale = Vector2(scaling, scaling)
	var texture = load("res://Assets/UI/Range Indicator.png")
	range_texture.texture = texture
	# Make the tower preview follow the mouse
	var control = Control.new()
	control.add_child(drag_tower, true)
	control.add_child(range_texture, true)
	control.position = mouse_position
	control.set_name("TowerPreview")
	add_child(control, true)
	# Ensure preview is shown above everything else
	move_child(get_node("TowerPreview"), 0)
	
func update_tower_preview(new_position, color):
	# Move preview and update color
	get_node("TowerPreview").position = new_position
	if get_node("TowerPreview/DragTower").modulate != Color(color):
		get_node("TowerPreview/DragTower").modulate = Color(color)
		get_node("TowerPreview/Sprite2D").modulate = Color(color)

func update_health_bar(base_health):
	# Update and animate health bar
	if current_tween:
		current_tween.kill()
	
	current_tween = create_tween()
	current_tween.tween_property(health_bar, "value", base_health, 0.15).set_trans(Tween.TRANS_LINEAR).set_ease(Tween.EASE_IN_OUT)
	# Emit game over if health reaches zero
	if base_health <= 0:
		game_finished.emit(lose)


func _on_pause_play_pressed() -> void:
	
	if get_tree().is_paused():
		# Unpause game
		get_tree().paused = false
		$HUD/PausePlay/AnimationPlayer.stop()
		$HUD/PauseMenu.hide()
	elif get_parent().current_wave == 0:
		# Start first wave and log telemetry event
		$HUD/PausePlay/AnimationPlayer.stop()
		get_parent().current_wave += 1
		get_parent().start_next_wave()
		Telemetry.log_event("stage_start", {})
	else:
		# Pause game
		get_tree().paused = true
		$HUD/PausePlay/AnimationPlayer.play("pulse")
		$HUD/PauseMenu.show()

func _on_quit_button_pressed() -> void:
	Telemetry.log_event("stage_quit", {})
	GameData.reset()
	get_tree().paused = false
	get_tree().change_scene_to_file("res://Scenes/scene_handler.tscn")


func _on_move_button_pressed() -> void:
	if tower_build_panel_shown:
		$HUD/TowerBuildPanel/AnimationPlayer.play("right")
		tower_build_panel_shown = false
	elif tower_build_panel_shown == false:
		$HUD/TowerBuildPanel/AnimationPlayer.play("left")
		tower_build_panel_shown = true


func _on_triangle_stock_pressed() -> void:
	if tower_build_panel_shown:
		$HUD/TowerBuildPanel/AnimationPlayer.play("right")
		tower_build_panel_shown = false
	elif tower_build_panel_shown == false:
		$HUD/TowerBuildPanel/AnimationPlayer.play("left")
		tower_build_panel_shown = true


func _on_star_stock_pressed() -> void:
	if tower_build_panel_shown:
		$HUD/TowerBuildPanel/AnimationPlayer.play("right")
		tower_build_panel_shown = false
	elif tower_build_panel_shown == false:
		$HUD/TowerBuildPanel/AnimationPlayer.play("left")
		tower_build_panel_shown = true


func _on_square_stock_pressed() -> void:
	if tower_build_panel_shown:
		$HUD/TowerBuildPanel/AnimationPlayer.play("right")
		tower_build_panel_shown = false
	elif tower_build_panel_shown == false:
		$HUD/TowerBuildPanel/AnimationPlayer.play("left")
		tower_build_panel_shown = true
