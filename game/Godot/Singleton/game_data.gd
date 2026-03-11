extends Node

# Signal for when the game ends
signal game_finished(result)

# Win or Lose variables
var lose = "lose"
var win = "win"

# Data for telemetry
var current_stage

# Multipliers
var enemy_damage_multiplier := 1.0
var enemy_speed_multiplier := 1.0
var money_earned_multiplier := 1.0

var triangle_radius_multiplier := 1.0
var star_radius_multiplier := 1.0


func update_data() -> void:
	# Get damage multiplier from database
	var json = await Telemetry.get_parameter("enemy_damage_multiplier")
	enemy_damage_multiplier = json[0]["value"]

	# Get speed multiplier from database
	json = await Telemetry.get_parameter("enemy_speed_multiplier")
	enemy_speed_multiplier = json[0]["value"]

	# Get money earned multiplier from database
	json = await Telemetry.get_parameter("money_earned_multiplier")
	money_earned_multiplier = json[0]["value"]

	# Get triangle radius multiplier from database
	json = await Telemetry.get_parameter("triangle_radius_multiplier")
	triangle_radius_multiplier = json[0]["value"]

	# Get star radius multiplier from database
	json = await Telemetry.get_parameter("star_radius_multiplier")
	star_radius_multiplier = json[0]["value"]

	enemy_data = {
		"medium_circle": {
			"health": 50,
			"speed": 500 * enemy_speed_multiplier,
			"cash": 100 * money_earned_multiplier,
			"damage": 10 * enemy_damage_multiplier
		},
		"large_circle": {
			"health": 170,
			"speed": 30 * enemy_speed_multiplier,
			"cash": 250 * money_earned_multiplier,
			"damage": 20 * enemy_damage_multiplier
		},
		"small_circle": {
			"health": 40,
			"speed": 80 * enemy_speed_multiplier,
			"cash": 80 * money_earned_multiplier,
			"damage": 5 * enemy_damage_multiplier
		}
	}

	tower_data["triangle_stock"]["range"] = 350 * triangle_radius_multiplier
	tower_data["triangle_t_2"]["range"] = 350 * triangle_radius_multiplier
	tower_data["triangle_t_3"]["range"] = 350 * triangle_radius_multiplier
	tower_data["star_stock"]["range"] = 400 * star_radius_multiplier
	tower_data["star_t_2"]["range"] = 500 * star_radius_multiplier
	tower_data["star_t_3"]["range"] = 600 * star_radius_multiplier
	
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

### Tower Data ####
var tower_data = {
	"triangle_stock": {
		"damage": 20,
		"rof": 3,
		"range": 350,
		"cost": 250},
	"triangle_t_2": {
		"damage": 40,
		"rof": 1,
		"range": 350},
	"triangle_t_3": {
		"damage": 60,
		"rof": 1,
		"range": 350},
	"square_stock": {
		"damage": 35,
		"rof": 1,
		"range": 10000,
		"cost": 550},
	"square_t_2": {
		"damage": 35,
		"rof": 1,
		"range": 10000},
	"square_t_3": {
		"damage": 35,
		"rof": 1,
		"range": 10000},
	"star_stock": {
		"damage": 5,
		"rof": 1.5,
		"range": 400,
		"cost": 550},
	"star_t_2": {
		"damage": 10,
		"rof": 1.5,
		"range": 500},
	"star_t_3": {
		"damage": 15,
		"rof": 1.5,
		"range": 600}
	}

# Tower Upgrade Panel Info
var tower_upgrades = {
	"TriangleStock": {
		"stage": 1,
		"1": "Pew Pew",
		"1desc": "+1 shot",
		"1cost": 400
	},
	"TriangleT2": {
		"stage": 2,
		"1": "Pew Pew Pew",
		"1desc": "+1 shot",
		"1cost": 700
	},
	"TriangleT3": {
		"stage": 3,
	},
	"SquareStock": {
		"stage": 1,
		"1": "Radial Sweep",
		"1desc": "Double projectiles",
		"1cost": 300
	},
	"SquareT2": {
		"stage": 2,
		"1": "Radial Sweep 2.0",
		"1desc": "Double Projectiles",
		"1cost": 800
	},
	"SquareT3": {
		"stage": 3
	},
	"StarStock": {
		"stage": 1,
		"1": "Supernova",
		"1desc": "+ damage & range",
		"1cost": 550
	},
	"StarT2": {
		"stage": 2,
		"1": "Blackhole",
		"1desc": "++ damage & range",
		"1cost": 1000
	},
	"StarT3": {
		"stage": 3
	}
	
}

#### Enemy Data ####
var enemy_data = {
	"medium_circle": {
		"health": 50,
		"speed": 60,
		"cash": 100,
		"damage": 10
	},
	"large_circle": {
		"health": 170,
		"speed": 30,
		"cash": 250,
		"damage": 20
	},
	"small_circle": {
		"health": 40,
		"speed": 80,
		"cash": 80,
		"damage": 5
	}
}

#### Level Data ####
var level_data = {
	"Level1": {
		"number_of_waves": 2,
		"wave_1": [["medium_circle", 1], ["medium_circle", 1]],
		"wave_2": [["large_circle", 1], ["large_circle", 1], ["large_circle", 1], ["large_circle", 1]]
	},
	"Level2": {
		"number_of_waves": 3,
		"wave_1": [["medium_circle", 1], ["medium_circle", 1]],
		"wave_2": [["large_circle", 1], ["large_circle", 1]],
		"wave_3": [["small_circle", 1], ["small_circle", 1]]
	},
	"Level3": {
		"number_of_waves": 3,
		"wave_1": [["medium_circle", 1], ["medium_circle", 1]],
		"wave_2": [["large_circle", 1], ["large_circle", 1]],
		"wave_3": [["small_circle", 1], ["small_circle", 1]]
	},
	"Level4": {
		"number_of_waves": 3,
		"wave_1": [["medium_circle", 1], ["medium_circle", 1]],
		"wave_2": [["large_circle", 1], ["large_circle", 1]],
		"wave_3": [["small_circle", 1], ["small_circle", 1]]
	},
	"Level5": {
		"number_of_waves": 3,
		"wave_1": [["medium_circle", 1], ["medium_circle", 1]],
		"wave_2": [["large_circle", 1], ["large_circle", 1]],
		"wave_3": [["small_circle", 1], ["small_circle", 1]]
	},
	"Level6": {
		"number_of_waves": 3,
		"wave_1": [["medium_circle", 1], ["medium_circle", 1]],
		"wave_2": [["large_circle", 1], ["large_circle", 1]],
		"wave_3": [["small_circle", 1], ["small_circle", 1]]
	},
	"Level7": {
		"number_of_waves": 3,
		"wave_1": [["medium_circle", 1], ["medium_circle", 1]],
		"wave_2": [["large_circle", 1], ["large_circle", 1]],
		"wave_3": [["small_circle", 1], ["small_circle", 1]]
	},
	"Level8": {
		"number_of_waves": 3,
		"wave_1": [["medium_circle", 1], ["medium_circle", 1]],
		"wave_2": [["large_circle", 1], ["large_circle", 1]],
		"wave_3": [["small_circle", 1], ["small_circle", 1]]
	},
	"Level9": {
		"number_of_waves": 3,
		"wave_1": [["medium_circle", 1], ["medium_circle", 1]],
		"wave_2": [["large_circle", 1], ["large_circle", 1]],
		"wave_3": [["small_circle", 1], ["small_circle", 1]]
	},
	"Level10": {
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
