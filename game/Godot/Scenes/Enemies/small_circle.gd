extends PathFollow2D

var speed = GameData.enemy_data["small_circle"]["speed"]

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _physics_process(delta: float) -> void:
	move(delta)

func move(delta):
	progress += speed * delta
