extends CanvasLayer

# Connect nodes
@onready var health_bar: TextureProgressBar = $HUD/HealthUI/HBoxContainer/HealthBar
@onready var cash: Label = $HUD/CashUI/HBoxContainer/Cash

var current_tween: Tween
var lose

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

func update_money(amount: int):
	# Update displayed cash
	cash.text = str(amount)

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
	var texture = load("res://Assets/Range Indicator.png")
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
	
	$HUD/PausePlay/AnimationPlayer.stop()
	if get_tree().is_paused():
		# Unpause game
		get_tree().paused = false
	elif get_parent().current_wave == 0:
		# Start first wave and log telemetry event
		get_parent().current_wave += 1
		get_parent().start_next_wave()
		Telemetry.log_event("stage_start", {})
	else:
		# Pause game
		get_tree().paused = true
