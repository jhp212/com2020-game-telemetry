extends PathFollow2D

# Load enemy stats from GameData
var speed = GameData.enemy_data["medium_circle"]["speed"]
var health =  GameData.enemy_data["medium_circle"]["health"]
var damage =  GameData.enemy_data["medium_circle"]["damage"]

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
		GameData.add_money(GameData.enemy_data["medium_circle"]["cash"])
		Telemetry.log_event("enemy_defeated", {"enemy_id": 2})
	$Body/AnimatedSprite2D.play("death")
	await $Body/AnimatedSprite2D.animation_finished
	enemy_death.emit()
	self.queue_free()

func _physics_process(delta: float) -> void:
	if health < GameData.enemy_data["medium_circle"]["health"] * 0.75 and health >= GameData.enemy_data["medium_circle"]["health"] * 0.5:
		$Body/AnimatedSprite2D.play("75%health")
	elif health < GameData.enemy_data["medium_circle"]["health"] * 0.5 and health >= GameData.enemy_data["medium_circle"]["health"] * 0.25:
		$Body/AnimatedSprite2D.play("50%health")
	elif health < GameData.enemy_data["medium_circle"]["health"] * 0.25 and health > 0:
		$Body/AnimatedSprite2D.play("25%health")

	if progress_ratio == 1.0:
		# Do damage to the player if enemy reaches the end of the path and die
		enemy_damage.emit(damage)
		die(1)
	move(delta)


func move(delta):
	# Move along the path
	progress += speed * delta
