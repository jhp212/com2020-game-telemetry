extends PathFollow2D

var speed = GameData.enemy_data["medium_circle"]["speed"]
var health =  GameData.enemy_data["medium_circle"]["health"]
var damage =  GameData.enemy_data["medium_circle"]["damage"]



# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.

func on_hit(damage):
	health -= damage
	if health <= 0:
		die()

func die():
	GameData.add_money(GameData.enemy_data["medium_circle"]["cash"])
	self.queue_free()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _physics_process(delta: float) -> void:
	#if unit_progress == 1.0:
	#	emit_signal("damage", damage)
	#	queue_free()
	move(delta)

func move(delta):
	progress += speed * delta
