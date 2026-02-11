extends Node

# Signal for when the game ends
signal game_finished(result)

# Win or Lose variables
var lose = "lose"
var win = "win"

# Data for telemetry
var user_id = randi_range(0, 1000)
var current_stage

# Damage multiplier
var enemy_damage_multiplier := 1.0



func _ready() -> void:
	# Get damage multiplier from database
	var json = await Telemetry.get_parameter("enemy_damage_multiplier")
	enemy_damage_multiplier = json[0]["value"]
	enemy_data = {
		"medium_circle": {
			"health": 50,
			"speed": 500,
			"cash": 100,
			"damage": 70 * enemy_damage_multiplier
		},
		"large_circle": {
			"health": 170,
			"speed": 30,
			"cash": 250,
			"damage": 5 * enemy_damage_multiplier
		},
		"small_circle": {
			"health": 40,
			"speed": 80,
			"cash": 80,
			"damage": 1 * enemy_damage_multiplier
		}
	}

#### tracking number of enemies ####
# Number of enemies currently in game
var enemy_amount = 0

func add_enemy_amount(number_of_enemies):
	# Increase the tracking number of enemies currently in game
	enemy_amount += number_of_enemies
	print("more are added: " + str(enemy_amount))

func remove_enemy_amount():
	# Decrease the tracking number of enemies currently in game
	enemy_amount -= 1
	print(str(enemy_amount))

#### Player Health ####
# players health
var base_health = 100

# Signal for when the players health changes
signal base_health_changed(new_health)

func damage_base(amount):
	# Decrease the players health and log telemetry event
	base_health -= amount
	base_health = max(base_health, 0)
	base_health_changed.emit(base_health)
	if base_health == 0:
		game_finished.emit(lose)
	Telemetry.log_event("damage_taken", {"amount": amount, "remaining_health": base_health})

#### Money ####
# Players money
var money :=2000

# Signal for when the players money amount changes
signal money_changed(new_amount)

func can_afford(amount):
	# Check if the player has enough money
	return money >= amount

func spend(amount):
	# Remove cost from players money and log telemetry event
	if not can_afford(amount):
		print("Not enough money")
		return false
	money -= amount
	money_changed.emit(money)
	Telemetry.log_event("money_spent", {"amount": amount, "remaining_amount": money})
	return true

func add_money(amount):
	# Add to players money
	money += amount
	money_changed.emit(money)
	print(money)

#### Tower Data ####
var tower_data = {
	"triangle_stock": {
		"damage": 20,
		"rof": 3,
		"range": 350,
		"cost": 250},
	"square_stock": {
		"damage": 35,
		"rof": 1,
		"range": 10000,
		"cost": 550},
	"star_stock": {
		"damage": 30,
		"rof": 1.5,
		"range": 10000,
		"cost": 550}
	}

#### Enemy Data ####
var enemy_data = {
	"medium_circle": {
		"health": 50,
		"speed": 500,
		"cash": 100,
		"damage": 70 * enemy_damage_multiplier
	},
	"large_circle": {
		"health": 170,
		"speed": 30,
		"cash": 250,
		"damage": 5 * enemy_damage_multiplier
	},
	"small_circle": {
		"health": 40,
		"speed": 80,
		"cash": 80,
		"damage": 1 * enemy_damage_multiplier
	}
}

#### Level Data ####
var level_data = {
	"Level1": {
		"number_of_waves": 2,
		"wave_1": [["medium_circle", 1], ["medium_circle", 1]],
		"wave_2": [["medium_circle", 1], ["medium_circle", 1]]
	},
	"Level2": {
		"number_of_waves": 3,
		"wave_1": [["medium_circle", 1], ["medium_circle", 1]],
		"wave_2": [["large_circle", 1], ["large_circle", 1]],
		"wave_3": [["small_circle", 1], ["small_circle", 1]]
	}
}
	


func reset():
	# Reset game data
	base_health = 100
	money = 850
	enemy_amount = 0
