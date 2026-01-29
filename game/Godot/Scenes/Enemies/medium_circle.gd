extends PathFollow2D

var speed = GameData.enemy_data["medium_circle"]["speed"]
var health =  GameData.enemy_data["medium_circle"]["health"]

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.

func on_hit(damage):
	health -= damage
	if health <= 0:
		die()

func die():
	self.queue_free()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _physics_process(delta: float) -> void:
	move(delta)

func move(delta):
	progress += speed * delta
