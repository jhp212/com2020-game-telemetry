extends Node2D

# Signal tower being clicked
signal tower_clicked(tower)

# Track enemies
var enemy_array = []
var enemy

# Tower state
var built = false
var ready_to_shoot = true

# Assign tower type
var tower_type := "SquareStock"

# Connect nodes
@onready var shoot_position_1: Marker2D = $Body/ShootPosition1
@onready var shoot_position_2: Marker2D = $Body/ShootPosition2
@onready var shoot_position_3: Marker2D = $Body/ShootPosition3
@onready var shoot_position_4: Marker2D = $Body/ShootPosition4
@onready var collision_shape: CollisionShape2D = $Range/CollisionShape2D
@onready var shoot_sfx: AudioStreamPlayer = $ShootSfx
@onready var placement_sfx: AudioStreamPlayer = $PlacementSfx

# Connect projectile scene
const projectile_square_scene = preload("res://Scenes/Towers/Projectiles/projectile_square.tscn")

func _physics_process(delta):
	# Act if enemies are in range and tower is built
	if enemy_array.size() != 0 and built:
		if ready_to_shoot:
			fire()
	else:
		enemy = null

func fire():
	ready_to_shoot = false
	shoot_sfx.play()
	
	#instance a projectile
	var new_projectile_1 = projectile_square_scene.instantiate()
	new_projectile_1.global_position = shoot_position_1.global_position
	new_projectile_1.global_rotation = shoot_position_1.global_rotation
	get_parent().add_child(new_projectile_1)
	
	
	
	var new_projectile_2 = projectile_square_scene.instantiate()
	new_projectile_2.global_position = shoot_position_2.global_position
	new_projectile_2.global_rotation = shoot_position_2.global_rotation
	get_parent().add_child(new_projectile_2)
	

	
	var new_projectile_3 = projectile_square_scene.instantiate()
	new_projectile_3.global_position = shoot_position_3.global_position
	new_projectile_3.global_rotation = shoot_position_3.global_rotation
	get_parent().add_child(new_projectile_3)
	
	
	
	var new_projectile_4 = projectile_square_scene.instantiate()
	new_projectile_4.global_position = shoot_position_4.global_position
	new_projectile_4.global_rotation = shoot_position_4.global_rotation
	get_parent().add_child(new_projectile_4)
	
	await get_tree().create_timer(GameData.tower_data["square_stock"]["rof"]).timeout
	ready_to_shoot = true

func _ready():
	# Connect the ClickArea's input event so the tower detects when its been clicked
	$ClickArea.input_event.connect(_on_click_area_input_event)
	# Set size of the range and log telemetry event
	if built:
		placement_sfx.play()
		collision_shape.shape.radius = GameData.tower_data["square_stock"]["range"]
		Telemetry.log_event("tower_spawn", {"tower_id": 2})

func _on_range_body_entered(body: Node2D) -> void:
	# Add enemy when it enters the range
	enemy_array.append(body.get_parent())

func _on_range_body_exited(body: Node2D) -> void:
	# Remove enemy when it leaves the range
	enemy_array.erase(body.get_parent())

func _on_click_area_input_event(viewport,event, shape_idx):
	# Check if the tower has been clicked and send signal
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		tower_clicked.emit(self)

func upgrade(tower):
	if tower == self:
		var upgraded_tower = load("res://Scenes/Towers/square_t_2.tscn")
		var upgraded = upgraded_tower.instantiate()
		
		upgraded.position = position
		upgraded.built = true
		
		get_parent().add_child(upgraded)
		queue_free()
		
		return upgraded

func sold():
	self.queue_free()
