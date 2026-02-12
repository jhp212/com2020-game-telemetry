extends PathFollow2D

# Load enemy stats from GameData
var speed = GameData.enemy_data["large_circle"]["speed"]
var health =  GameData.enemy_data["large_circle"]["health"]
var damage =  GameData.enemy_data["large_circle"]["damage"]

# Signals for when the enemy deals damage or dies
signal enemy_damage(damage)
signal enemy_death()



func on_hit(damage):
	# Reduce health when hit
	health -= damage
	if health <= 0:
		die(0)

func die(condition):
	# condition 0 = killed by player
	# condition 1 = reached the end of the path
	if condition == 0:
		# Give money to player and log telemetry event
		GameData.add_money(GameData.enemy_data["large_circle"]["cash"])
		Telemetry.log_event("enemy_defeated", {"enemy_id": 3})
		enemy_death.emit()
	if condition == 1:
		# Emit death signal and log telemetry event, then remove enemy
		enemy_death.emit()
	self.queue_free()

func _physics_process(delta: float) -> void:
	if progress_ratio == 1.0:
		# Do damage to the player if enemy reaches the end of the path and die
		enemy_damage.emit(damage)
		die(1)
	move(delta)

func move(delta):
	# Move along the path
	progress += speed * delta
