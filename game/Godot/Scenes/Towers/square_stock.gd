extends Node2D

var enemy_array = []
var built = false
var enemy
var ready_to_shoot = true

@onready var shoot_position_1: Marker2D = $Body/ShootPosition1
@onready var shoot_position_2: Marker2D = $Body/ShootPosition2
@onready var shoot_position_3: Marker2D = $Body/ShootPosition3
@onready var shoot_position_4: Marker2D = $Body/ShootPosition4
@onready var collision_shape: CollisionShape2D = $Range/CollisionShape2D

const projectile_square_scene = preload("res://Scenes/Towers/Projectiles/projectile_square.tscn")

func _physics_process(delta):
	if enemy_array.size() != 0 and built:
		if ready_to_shoot:
			fire()
	else:
		enemy = null

func fire():
	ready_to_shoot = false
	
	#instance a projectile
	var new_projectile_1 = projectile_square_scene.instantiate()
	new_projectile_1.global_position = shoot_position_1.global_position
	new_projectile_1.global_rotation = shoot_position_1.global_rotation
	get_parent().add_child(new_projectile_1)
	
	
	
	var new_projectile_2 = projectile_square_scene.instantiate()
	new_projectile_2.global_position = shoot_position_2.global_position
	new_projectile_2.global_rotation = shoot_position_2.global_rotation
	get_parent().add_child(new_projectile_2)
	

	
	var new_projectile_3 = projectile_square_scene.instantiate()
	new_projectile_3.global_position = shoot_position_3.global_position
	new_projectile_3.global_rotation = shoot_position_3.global_rotation
	get_parent().add_child(new_projectile_3)
	
	
	
	var new_projectile_4 = projectile_square_scene.instantiate()
	new_projectile_4.global_position = shoot_position_4.global_position
	new_projectile_4.global_rotation = shoot_position_4.global_rotation
	get_parent().add_child(new_projectile_4)
	
	await get_tree().create_timer(GameData.tower_data["square_stock"]["rof"]).timeout
	ready_to_shoot = true

func _init():
	pass
	
func _ready():
	if built:
		collision_shape.shape.radius = GameData.tower_data["square_stock"]["range"]
		Telemetry.log_event("tower_spawn", {"tower_id": 2})
	
	
func _process(delta):
	pass
	



func _on_range_body_entered(body: Node2D) -> void:
	enemy_array.append(body.get_parent())
	print("bababoowee")


func _on_range_body_exited(body: Node2D) -> void:
	enemy_array.erase(body.get_parent())
