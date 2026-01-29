extends Node2D

var enemy_array = []
var built = false

@onready var collision_shape: CollisionShape2D = $Range/CollisionShape2D

func _physics_process(delta):
	turn()

func turn():
	var enemy_position = get_global_mouse_position()
	get_node("Body").look_at(enemy_position)

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
