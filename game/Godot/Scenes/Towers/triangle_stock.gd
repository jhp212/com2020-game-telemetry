extends Node2D

# Enemy tracking
var enemy_array = []
var enemy

# Tower state
var built = false
var ready_to_shoot = true

# Connect nodes
@onready var collision_shape: CollisionShape2D = $Range/CollisionShape2D
@onready var shoot_position: Marker2D = $Body/ShootPosition

func _physics_process(delta):
	# Act if enemies are in range and tower is built
	if enemy_array.size() != 0 and built:
		select_enemy()
		turn()
		if ready_to_shoot:
			fire()
	else:
		enemy = null

func select_enemy():
	# Select enemy that's furthest along the path
	var enemy_progress_array = []
	for i in enemy_array:
		enemy_progress_array.append(i.progress)
	var max_progress = enemy_progress_array.max()
	var enemy_index = enemy_progress_array.find(max_progress)
	enemy = enemy_array[enemy_index]
	

func turn():
	# Turn tower to face slected enemy
	get_node("Body").look_at(enemy.position)

func fire():
	# Shoot and deal damage to the enemy
	ready_to_shoot = false
	apply_recoil()
	enemy.on_hit(GameData.tower_data["triangle_stock"]["damage"])
	# Wait for the rof cooldown before being able to shoot again
	await get_tree().create_timer(GameData.tower_data["triangle_stock"]["rof"]).timeout
	ready_to_shoot = true
	

func apply_recoil():
	# Small movement backwards when it shoots
	var body := $Body
	var recoil_distance := 8.0
	var recoil_time := 0.04

	var recoil_dir = -body.transform.x
	var start_pos = body.position
	var recoil_pos = start_pos + recoil_dir * recoil_distance

	var tween = create_tween()
	tween.tween_property(body, "position", recoil_pos, recoil_time)
	tween.tween_property(body, "position", start_pos, recoil_time)

func _ready():
	# Set size of the range and log telemetry event
	if built:
		collision_shape.shape.radius = GameData.tower_data["triangle_stock"]["range"] / 2
		Telemetry.log_event("tower_spawn", {"tower_id": 1})

func _on_range_body_entered(body: Node2D) -> void:
	# Add enemy when it enters the range
	enemy_array.append(body.get_parent())
	print(enemy_array)

func _on_range_body_exited(body: Node2D) -> void:
	# Remove enemy when it leaves the range
	enemy_array.erase(body.get_parent())
