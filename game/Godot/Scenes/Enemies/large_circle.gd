extends PathFollow2D

var speed = GameData.enemy_data["large_circle"]["speed"]
var health =  GameData.enemy_data["large_circle"]["health"]
var damage =  GameData.enemy_data["large_circle"]["damage"]

signal enemy_damage(damage)
signal enemy_death()

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.

func on_hit(damage):
	health -= damage
	if health <= 0:
		die()

func die():
	GameData.add_money(GameData.enemy_data["medium_circle"]["cash"])
	enemy_death.emit()
	self.queue_free()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _physics_process(delta: float) -> void:
	if progress_ratio == 1.0:
		enemy_damage.emit(damage)
		queue_free()
	move(delta)

func move(delta):
	progress += speed * delta
