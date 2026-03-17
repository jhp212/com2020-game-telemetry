extends Node2D

# Signal tower being clicked
signal tower_clicked(tower)

# Enemy tracking
var enemy_array = []
var enemy

# Tower state
var built = false
var ready_to_shoot = true

var spin_speed = 2

# Assign tower type
var tower_type := "StarT3"

# Connect nodes
@onready var collision_shape: CollisionShape2D = $Range/CollisionShape2D
@onready var body: Sprite2D = $Body
@onready var placement_sfx: AudioStreamPlayer = $PlacementSfx

func _physics_process(delta):
	# Act if enemies are in range and tower is built
	if enemy_array.size() != 0 and built:
		body.rotation += spin_speed * delta
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

func fire():
	# Shoot and deal damage to the enemy
	ready_to_shoot = false
	for enemy in enemy_array:
		enemy.on_hit(GameData.tower_data["star_t_3"]["damage"])
	# Wait for the rof cooldown before being able to shoot again
	await get_tree().create_timer(GameData.tower_data["triangle_t_3"]["rof"]).timeout
	ready_to_shoot = true

func _ready():
	# Connect the ClickArea's input event so the tower detects when its been clicked
	$ClickArea.input_event.connect(_on_click_area_input_event)
	# Set size of the range and log telemetry event
	if built:
		placement_sfx.play()
		collision_shape.shape.radius = GameData.tower_data["star_t_3"]["range"] / 2
		Telemetry.log_event("tower_upgraded", {"tower_id": 3})

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
		var upgraded_tower = load("res://Scenes/Towers/star_t_3.tscn")
		var upgraded = upgraded_tower.instantiate()
		
		upgraded.position = position
		upgraded.built = true
		
		get_parent().add_child(upgraded)
		queue_free()
		
		return upgraded

func sold():
	self.queue_free()
