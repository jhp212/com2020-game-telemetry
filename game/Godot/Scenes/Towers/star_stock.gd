extends Node2D

var enemy_array = []
var built = false
var enemy
var ready_to_shoot = true
var spin_speed = 1

@onready var shoot_position_1: Marker2D = $Body/ShootPosition1
@onready var shoot_position_2: Marker2D = $Body/ShootPosition2
@onready var shoot_position_3: Marker2D = $Body/ShootPosition3
@onready var shoot_position_4: Marker2D = $Body/ShootPosition4
@onready var shoot_position_5: Marker2D = $Body/ShootPosition5
@onready var collision_shape: CollisionShape2D = $Range/CollisionShape2D
@onready var body: Sprite2D = $Body

const projectile_star_scene = preload("res://Scenes/Towers/Projectiles/projectile_star.tscn")


func _physics_process(delta):
	if enemy_array.size() != 0 and built:
		body.rotation += spin_speed * delta
		if ready_to_shoot:
			fire()
	else:
		enemy = null

func fire():
	ready_to_shoot = false
	
	#instance a projectile
	var new_projectile_1 = projectile_star_scene.instantiate()
	new_projectile_1.global_position = shoot_position_1.global_position
	new_projectile_1.global_rotation = shoot_position_1.global_rotation
	get_parent().add_child(new_projectile_1)
	
	var new_projectile_2 = projectile_star_scene.instantiate()
	new_projectile_2.global_position = shoot_position_2.global_position
	new_projectile_2.global_rotation = shoot_position_2.global_rotation
	get_parent().add_child(new_projectile_2)
	
	var new_projectile_3 = projectile_star_scene.instantiate()
	new_projectile_3.global_position = shoot_position_3.global_position
	new_projectile_3.global_rotation = shoot_position_3.global_rotation
	get_parent().add_child(new_projectile_3)
	
	var new_projectile_4 = projectile_star_scene.instantiate()
	new_projectile_4.global_position = shoot_position_4.global_position
	new_projectile_4.global_rotation = shoot_position_4.global_rotation
	get_parent().add_child(new_projectile_4)
	
	var new_projectile_5 = projectile_star_scene.instantiate()
	new_projectile_5.global_position = shoot_position_5.global_position
	new_projectile_5.global_rotation = shoot_position_5.global_rotation
	get_parent().add_child(new_projectile_5)
	
	#enemy.on_hit(GameData.tower_data["square_stock"]["damage"])
	await get_tree().create_timer(GameData.tower_data["star_stock"]["rof"]).timeout
	ready_to_shoot = true

func _init():
	pass
	
func _ready():
	if built:
		collision_shape.shape.radius = GameData.tower_data["star_stock"]["range"]
	
func _process(delta):
	pass
	


func _on_range_body_entered(body: Node2D) -> void:
	enemy_array.append(body.get_parent())
	print(enemy_array)


func _on_range_body_exited(body: Node2D) -> void:
	enemy_array.erase(body.get_parent())
