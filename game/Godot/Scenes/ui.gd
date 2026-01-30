extends CanvasLayer

@onready var health_bar: TextureProgressBar = $HUD/HealthUI/HBoxContainer/HealthBar
@onready var cash: Label = $HUD/CashUI/HBoxContainer/Cash


func _ready():
	GameData.money_changed.connect(update_money)
	update_money(GameData.money)

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

#func update_health_bar(base_health):
#	hp_bar_tween.interpolate_property(health_bar, 'value', health_bar.value, base_health, 0.1, Tween.TRANS_LINEAR, Tween.EASE_IN_OUT)
##	health_bar_tween.start()
#	if base_health >= 60:
#		health_bar.set_tint_progress("3cc510")
#	elif base_health <= 60 and base_health >= 25:
#		health_bar.set_tint_progress("e1be32")
#	else:
#		health_bar.set_tinit_progress("e11e1e")
