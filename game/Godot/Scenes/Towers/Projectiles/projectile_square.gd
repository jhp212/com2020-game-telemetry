extends Node2D

# Connect nodes
@onready var body: Sprite2D = $Body
@onready var Glow: Sprite2D = $Glow
@onready var AnimPlayer: AnimationPlayer = $AnimationPlayer
@onready var area: Area2D = $Area

# Tracking enemies in range
var enemy_array = []
var enemy

# Movement variables
var speed: float = 300
var spin_speed = 15



func _process(delta: float) -> void:
	# Constantly spin
	body.rotation += spin_speed * delta

func _physics_process(delta: float) -> void:
	# Move in direction based on rotation
	global_position += Vector2(1,0).rotated(rotation) * speed * delta
	Glow.position = Vector2(0,0).rotated(-rotation)
	
func _on_animation_player_animation_finished(anim_name: StringName) -> void:
	# Remove projectile after "remove" animation ends
	if anim_name == "remove":
		queue_free()

func _on_distance_timeout_timeout() -> void:
	# Start "remove" animation if existed for too long
	AnimPlayer.play("remove")


func _on_area_body_entered(body: Node2D) -> void:
	# Detect collision with enemy
	var enemy = body.get_parent()
	if enemy.is_in_group("enemies"):
		enemy_array.append(enemy)
		enemy.on_hit(GameData.tower_data["square_stock"]["damage"])
		print("hit")
	queue_free()
	
