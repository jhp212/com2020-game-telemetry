extends Node2D

var enemy_array = []
var built = false
var enemy
var ready_to_shoot = true

@onready var collision_shape: CollisionShape2D = $Range/CollisionShape2D


func _physics_process(delta):
	if enemy_array.size() != 0 and built:
		select_enemy()
		turn()
		if ready_to_shoot:
			fire()
	else:
		enemy = null

func select_enemy():
	var enemy_progress_array = []
	for i in enemy_array:
		enemy_progress_array.append(i.progress)
	var max_progress = enemy_progress_array.max()
	var enemy_index = enemy_progress_array.find(max_progress)
	enemy = enemy_array[enemy_index]
	

func turn():
	get_node("Body").look_at(enemy.position)

func fire():
	ready_to_shoot = false
	enemy.on_hit(GameData.tower_data["triangle_stock"]["damage"])
	await get_tree().create_timer(GameData.tower_data["triangle_stock"]["rof"]).timeout
	ready_to_shoot = true



func _init():
	pass
	
func _ready():
	if built:
		collision_shape.shape.radius = GameData.tower_data["triangle_stock"]["range"] / 2
	
	
func _process(delta):
	pass
	


func _on_range_body_entered(body: Node2D) -> void:
	enemy_array.append(body.get_parent())
	print(enemy_array)


func _on_range_body_exited(body: Node2D) -> void:
	enemy_array.erase(body.get_parent())
