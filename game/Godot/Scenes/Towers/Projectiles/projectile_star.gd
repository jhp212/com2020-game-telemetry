extends Node2D

@onready var body: Sprite2D = $Body
@onready var Glow: Sprite2D = $Glow
@onready var AnimPlayer: AnimationPlayer = $AnimationPlayer
@onready var area: Area2D = $Area

var enemy_array = []
var enemy
var speed: float = 300
var spin_speed = 15


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass
	
func _process(delta: float) -> void:
	body.rotation += spin_speed * delta

func _physics_process(delta: float) -> void:
	global_position += Vector2(1,0).rotated(rotation) * speed * delta
	Glow.position = Vector2(0,0).rotated(-rotation)
	
func _on_animation_player_animation_finished(anim_name: StringName) -> void:
	if anim_name == "remove":
		queue_free()

func _on_distance_timeout_timeout() -> void:
	AnimPlayer.play("remove")


func _on_area_body_entered(body: Node2D) -> void:
	var enemy = body.get_parent()
	if enemy.is_in_group("enemies"):
		enemy_array.append(enemy)
		enemy.on_hit(GameData.tower_data["star_stock"]["damage"])
		print("hit")
	queue_free()
