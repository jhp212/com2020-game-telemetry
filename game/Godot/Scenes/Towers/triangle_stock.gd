extends Node2D

# Signal tower being clicked
signal tower_clicked(tower)

# Enemy tracking
var enemy_array = []
var enemy

# Tower state
var built = false
var ready_to_shoot = true

# Assign tower type
var tower_type := "TriangleStock"

# Connect nodes
@onready var collision_shape: CollisionShape2D = $Range/CollisionShape2D
@onready var shoot_position: Marker2D = $Body/ShootPosition
@onready var shoot_sfx: AudioStreamPlayer = $ShootSfx
@onready var placement_sfx: AudioStreamPlayer = $PlacementSfx

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
	shoot_sfx.play()
	apply_recoil()
	enemy.on_hit(GameData.tower_data["triangle_stock"]["damage"])
	# Wait for the rof cooldown before being able to shoot again
	await get_tree().create_timer(GameData.tower_data["triangle_stock"]["rof"]).timeout
	ready_to_shoot = true

func apply_recoil():
	# Small movement backwards when it shoots
	var body := $Body
	var recoil_distance := 8.0
	var recoil_time := 0.06

	var recoil_dir = -body.transform.x
	var start_pos = body.position
	var recoil_pos = start_pos + recoil_dir * recoil_distance

	var tween = create_tween()
	tween.tween_property(body, "position", recoil_pos, recoil_time)
	tween.tween_property(body, "position", start_pos, recoil_time)

func _ready():
	# Connect the ClickArea's input event so the tower detects when its been clicked
	$ClickArea.input_event.connect(_on_click_area_input_event)
	# Set size of the range and log telemetry event
	if built:
		# PLay sound effect when placed
		placement_sfx.play()
		collision_shape.shape.radius = GameData.tower_data["triangle_stock"]["range"] / 2
		Telemetry.log_event("tower_spawn", {"tower_id": 1})

func _on_range_body_entered(body: Node2D) -> void:
	# Add enemy when it enters the range
	enemy_array.append(body.get_parent())
	print(enemy_array)

func _on_range_body_exited(body: Node2D) -> void:
	# Remove enemy when it leaves the range
	enemy_array.erase(body.get_parent())

func _on_click_area_input_event(viewport,event, shape_idx):
	# Check if the tower has been clicked and send signal
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		tower_clicked.emit(self)

func upgrade(tower):
	print("upgraded")
	if tower == self:
		var upgraded_tower = load("res://Scenes/Towers/triangle_t_2.tscn")
		var upgraded = upgraded_tower.instantiate()
		
		upgraded.position = position
		upgraded.built = true
		
		get_parent().add_child(upgraded)
		queue_free()
		
		return upgraded

func sold():
	self.queue_free()
