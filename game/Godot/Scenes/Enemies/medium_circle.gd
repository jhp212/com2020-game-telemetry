extends PathFollow2D

var speed = GameData.enemy_data["medium_circle"]["speed"]
var health =  GameData.enemy_data["medium_circle"]["health"]
var damage =  GameData.enemy_data["medium_circle"]["damage"]

signal enemy_damage(damage)
signal enemy_death()

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.

func on_hit(damage):
	health -= damage
	if health <= 0:
		die(0)

func die(condition):
	if condition == 0:
		GameData.add_money(GameData.enemy_data["medium_circle"]["cash"])
		Telemetry.log_event("enemy_defeated", {"enemy_id": 2})
		enemy_death.emit()
	if condition == 1:
		enemy_death.emit()
		Telemetry.log_event("enemy_defeated", {"enemy_id": 2})
	self.queue_free()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _physics_process(delta: float) -> void:
	if progress_ratio == 1.0:
		enemy_damage.emit(damage)
		die(1)
	move(delta)


func move(delta):
	progress += speed * delta
