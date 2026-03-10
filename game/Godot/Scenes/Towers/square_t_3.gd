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
var tower_type := "SquareT3"

var shoot_position

# Connect nodes
@onready var shoot_position_1: Marker2D = $Body/ShootPosition1
@onready var shoot_position_2: Marker2D = $Body/ShootPosition2
@onready var shoot_position_3: Marker2D = $Body/ShootPosition3
@onready var shoot_position_4: Marker2D = $Body/ShootPosition4
@onready var shoot_position_5: Marker2D = $Body/ShootPosition5
@onready var shoot_position_6: Marker2D = $Body/ShootPosition6
@onready var shoot_position_7: Marker2D = $Body/ShootPosition7
@onready var shoot_position_8: Marker2D = $Body/ShootPosition8
@onready var shoot_position_9: Marker2D = $Body/ShootPosition9
@onready var shoot_position_10: Marker2D = $Body/ShootPosition10
@onready var shoot_position_11: Marker2D = $Body/ShootPosition11
@onready var shoot_position_12: Marker2D = $Body/ShootPosition12
@onready var shoot_position_13: Marker2D = $Body/ShootPosition13
@onready var shoot_position_14: Marker2D = $Body/ShootPosition14
@onready var shoot_position_15: Marker2D = $Body/ShootPosition15
@onready var shoot_position_16: Marker2D = $Body/ShootPosition16
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
	for pos in shoot_position:
		var new_projectile = projectile_square_scene.instantiate()
		new_projectile.global_position = pos.global_position
		new_projectile.global_rotation = pos.global_rotation
		get_parent().add_child(new_projectile)
	
	await get_tree().create_timer(GameData.tower_data["square_t_3"]["rof"]).timeout
	ready_to_shoot = true

func _ready():
	# Connect the ClickArea's input event so the tower detects when its been clicked
	$ClickArea.input_event.connect(_on_click_area_input_event)
	# Set size of the range and log telemetry event
	if built:
		placement_sfx.play()
		collision_shape.shape.radius = GameData.tower_data["square_t_3"]["range"]
		Telemetry.log_event("tower_upgraded", {"tower_id": 2})
		shoot_position = [shoot_position_1,
shoot_position_2,
shoot_position_3,
shoot_position_4,
shoot_position_5,
shoot_position_6,
shoot_position_7,
shoot_position_8,
shoot_position_9,
shoot_position_10,
shoot_position_11,
shoot_position_12,
shoot_position_13,
shoot_position_14,
shoot_position_15,
shoot_position_16,
]

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
		print("square clicvked")
