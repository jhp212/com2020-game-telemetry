extends Node2D

var enemy_array = []
var built = false
var enemy
var ready_to_shoot = true

@onready var shoot_position: Marker2D = $Body/ShootPosition
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
	var new_projectile = projectile_square_scene.instantiate()
	new_projectile.global_position = shoot_position.global_position
	new_projectile.global_rotation = shoot_position.global_rotation
	get_parent().add_child(new_projectile)
	
	#enemy.on_hit(GameData.tower_data["square_stock"]["damage"])
	await get_tree().create_timer(GameData.tower_data["square_stock"]["rof"]).timeout
	ready_to_shoot = true
	

func _init():
	pass
	
func _ready():
	if built:
		collision_shape.shape.radius = GameData.tower_data["square_stock"]["range"] / 2
	
	
func _process(delta):
	pass
	



func _on_range_body_entered(body: Node2D) -> void:
	enemy_array.append(body.get_parent())
	print(enemy_array)


func _on_range_body_exited(body: Node2D) -> void:
	enemy_array.erase(body.get_parent())
