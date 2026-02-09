extends CanvasLayer

@onready var health_bar: TextureProgressBar = $HUD/HealthUI/HBoxContainer/HealthBar
@onready var cash: Label = $HUD/CashUI/HBoxContainer/Cash

var current_tween: Tween

var lose
signal game_finished(result)

func _ready():
	self.show()
	GameData.base_health_changed.connect(update_health_bar)
	update_health_bar(GameData.base_health)
	GameData.money_changed.connect(update_money)
	update_money(GameData.money)
	$HUD/PausePlay/AnimationPlayer.play("pulse")

func update_money(amount: int):
	cash.text = str(amount)

func set_tower_preview(tower_type, mouse_position):
	var drag_tower = load("res://Scenes/Towers/" + tower_type + ".tscn").instantiate()
	drag_tower.set_name("DragTower")
	drag_tower.modulate = Color("8a8a8a")
	
	var range_texture = Sprite2D.new()
	range_texture.position = Vector2(0,0)
	var scaling = GameData.tower_data[tower_type]["range"] / 600.0
	range_texture.scale = Vector2(scaling, scaling)
	var texture = load("res://Assets/Range Indicator.png")
	range_texture.texture = texture
	
	var control = Control.new()
	control.add_child(drag_tower, true)
	control.add_child(range_texture, true)
	control.position = mouse_position
	control.set_name("TowerPreview")
	add_child(control, true)
	move_child(get_node("TowerPreview"), 0)
	
func update_tower_preview(new_position, color):
	get_node("TowerPreview").position = new_position
	if get_node("TowerPreview/DragTower").modulate != Color(color):
		get_node("TowerPreview/DragTower").modulate = Color(color)
		get_node("TowerPreview/Sprite2D").modulate = Color(color)

func update_health_bar(base_health):
	if current_tween:
		current_tween.kill()
	
	current_tween = create_tween()
	current_tween.tween_property(health_bar, "value", base_health, 0.15).set_trans(Tween.TRANS_LINEAR).set_ease(Tween.EASE_IN_OUT)
	
	if base_health <= 0:
		game_finished.emit(lose)


func _on_pause_play_pressed() -> void:
	$HUD/PausePlay/AnimationPlayer.stop()
	if get_tree().is_paused():
		get_tree().paused = false
	elif get_parent().current_wave == 0:
		get_parent().current_wave += 1
		get_parent().start_next_wave()
	else:
		get_tree().paused = true
