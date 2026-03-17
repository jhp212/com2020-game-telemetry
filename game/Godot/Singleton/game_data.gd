extends Node

# Signal for when the game ends
signal game_finished(result)

# Win or Lose variables
var lose = "lose"
var win = "win"

# Data for telemetry
var current_stage

# Handling difficulty
var game_difficulty = "medium"
var health_multiplier

# Multipliers
var enemy_damage_multiplier := 1.0
var enemy_speed_multiplier := 1.0
var money_earned_multiplier := 1.0

var triangle_radius_multiplier := 1.0
var star_radius_multiplier := 1.0


func _ready() -> void:
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
			"health": 40,
			"speed": 90 * enemy_speed_multiplier,
			"cash": 10 * money_earned_multiplier,
			"damage": 10 * enemy_damage_multiplier
		},
		"large_circle": {
			"health": 150,
			"speed": 60 * enemy_speed_multiplier,
			"cash": 30 * money_earned_multiplier,
			"damage": 20 * enemy_damage_multiplier,
		},
		"small_circle": {
			"health": 20,
			"speed": 140 * enemy_speed_multiplier,
			"cash": 20 * money_earned_multiplier,
			"damage": 5 * enemy_damage_multiplier
		},
		"mini_boss_circle": {
			"health": 1000,
			"speed": 50 * enemy_speed_multiplier,
			"cash": 150 * money_earned_multiplier,
			"damage": 70 * enemy_damage_multiplier
		},
		"big_boss_circle": {
			"health": 2000,
			"speed": 40 * enemy_speed_multiplier,
			"cash": 250 * money_earned_multiplier,
			"damage": 100 * enemy_damage_multiplier
		}
	}

	tower_data = {
		"triangle_stock": {
			"damage": 20,
			"rof": 1,
			"range": 350 * triangle_radius_multiplier,
			"cost": 250},
		"triangle_t_2": {
			"damage": 40,
			"rof": 1,
			"range": 350 * triangle_radius_multiplier},
		"triangle_t_3": {
			"damage": 60,
			"rof": 1,
			"range": 350 * triangle_radius_multiplier},
		"square_stock": {
			"damage": 25,
			"rof": 1,
			"range": 10000,
			"cost": 400},
		"square_t_2": {
			"damage": 25,
			"rof": 1,
			"range": 10000},
		"square_t_3": {
			"damage": 25,
			"rof": 1,
			"range": 10000},
		"star_stock": {
			"damage": 5,
			"rof": 1.5,
			"range": 400 * star_radius_multiplier,
			"cost": 550},
		"star_t_2": {
			"damage": 10,
			"rof": 1.5,
			"range": 500 * star_radius_multiplier},
		"star_t_3": {
			"damage": 15,
			"rof": 1.5,
			"range": 600 * star_radius_multiplier}
	}

func difficulty_selected(difficulty):
	enemy_data["medium_circle"]["health"] = 50
	enemy_data["small_circle"]["health"] = 200
	enemy_data["large_circle"]["health"] = 40
	enemy_data["mini_boss_circle"]["health"] = 1000
	enemy_data["big_boss_circle"]["health"] = 10000
	if difficulty == "easy":
		# Get easy enemy health multiplier from database
		var json = await Telemetry.get_parameter("easy_health_multiplier")
		health_multiplier = json[0]["value"]
	elif difficulty == "medium":
		# Get medium enemy health multiplier from database
		var json = await Telemetry.get_parameter("medium_health_multiplier")
		health_multiplier = json[0]["value"]
	elif difficulty == "hard":
		# Get hard enemy health multiplier from database
		var json = await Telemetry.get_parameter("hard_health_multiplier")
		health_multiplier = json[0]["value"]
	else:
		print("Invalid difficulty detected!")
	enemy_data["medium_circle"]["health"] = enemy_data["medium_circle"]["health"] * health_multiplier
	enemy_data["small_circle"]["health"] = enemy_data["small_circle"]["health"] * health_multiplier
	enemy_data["large_circle"]["health"] = enemy_data["large_circle"]["health"] * health_multiplier
	enemy_data["mini_boss_circle"]["health"] = enemy_data["mini_boss_circle"]["health"] * health_multiplier
	enemy_data["big_boss_circle"]["health"] = enemy_data["big_boss_circle"]["health"] * health_multiplier


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
var money := 850

# Signal for when the players money amount changes
signal money_changed(new_amount)

func can_afford(amount):
	# Check if the player has enough money
	return money >= amount

func spend(amount):
	# Remove cost from players money and log telemetry event
	if not can_afford(amount):
		return false
	money -= amount
	money_changed.emit(money)
	Telemetry.log_event("money_spent", {"amount": amount, "remaining_amount": money})
	return true

func add_money(amount):
	# Add to players money
	money += amount
	money_changed.emit(money)

#### Tower Data ####
# Parameters
var tower_data = {
	"triangle_stock": {
		"damage": 20,
		"rof": 1,
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
		"damage": 25,
		"rof": 1,
		"range": 10000,
		"cost": 400},
	"square_t_2": {
		"damage": 25,
		"rof": 1,
		"range": 10000},
	"square_t_3": {
		"damage": 25,
		"rof": 1,
		"range": 10000},
	"star_stock": {
		"damage": 5,
		"rof": 1.5,
		"range": 400 * star_radius_multiplier,
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
		"1cost": 400,
		"sell_price": 130
		
	},
	"TriangleT2": {
		"stage": 2,
		"1": "Pew Pew Pew",
		"1desc": "+1 shot",
		"1cost": 600,
		"sell_price": 330
	},
	"TriangleT3": {
		"stage": 3,
		"sell_price": 680
	},
	"SquareStock": {
		"stage": 1,
		"1": "Radial Sweep",
		"1desc": "Double projectiles",
		"1cost": 500,
		"sell_price": 280
	},
	"SquareT2": {
		"stage": 2,
		"1": "Radial Sweep 2.0",
		"1desc": "Double Projectiles",
		"1cost": 1400,
		"sell_price": 430
	},
	"SquareT3": {
		"stage": 3,
		"sell_price": 830
	},
	"StarStock": {
		"stage": 1,
		"1": "Supernova",
		"1desc": "+ damage & range",
		"1cost": 600,
		"sell_price": 280
	},
	"StarT2": {
		"stage": 2,
		"1": "Blackhole",
		"1desc": "++ damage & range",
		"1cost": 1000,
		"sell_price": 590
	},
	"StarT3": {
		"stage": 3,
		"sell_price": 1090
	}
	
}

#### Enemy Data ####
var enemy_data = {
	"medium_circle": {
		"health": 40,
		"speed": 90 * enemy_speed_multiplier,
		"cash": 10 * money_earned_multiplier,
		"damage": 10 * enemy_damage_multiplier
	},
	"large_circle": {
		"health": 150,
		"speed": 60 * enemy_speed_multiplier,
		"cash": 30 * money_earned_multiplier,
		"damage": 20 * enemy_damage_multiplier,
	},
	"small_circle": {
		"health": 20,
		"speed": 140 * enemy_speed_multiplier,
		"cash": 20 * money_earned_multiplier,
		"damage": 5 * enemy_damage_multiplier
	},
	"mini_boss_circle": {
		"health": 1000,
		"speed": 50 * enemy_speed_multiplier,
		"cash": 150 * money_earned_multiplier,
		"damage": 70 * enemy_damage_multiplier
	},
	"big_boss_circle": {
		"health": 2000,
		"speed": 40 * enemy_speed_multiplier,
		"cash": 250 * money_earned_multiplier,
		"damage": 100 * enemy_damage_multiplier
	}
}

#### Level Data ####
var lc = "large_circle"
var mc = "medium_circle"
var sc = "small_circle"
var mbc = "mini_boss_circle"
var bbc = "big_boss_circle"

var level_data = {
	"Level1": {
		"number_of_waves": 5,
		"wave_1": [[mc, 1], [mc, 1], [mc, 1], [mc, 1], [mc, 1]],
		"wave_2": [[sc, 1], [sc, 1], [sc, 1], [sc, 1], [sc, 1]],
		"wave_3": [[lc, 2], [lc, 2], [lc, 1]],
		"wave_4": [[sc, 1], [sc, 1], [sc, 1], [mc, 2], [mc, 2], [mc, 2], [lc, 3], [lc, 3], [lc, 1]],  
		"wave_5": [[mbc, 1]],
	},
	"Level2": {
		"number_of_waves": 10,
		"wave_1": [[mc, 1], [mc, 1], [mc, 1], [mc, 1], [mc, 1]],
		"wave_2": [[sc, 1], [sc, 1], [sc, 1], [sc, 1], [sc, 1]],
		"wave_3": [[lc, 2], [lc, 2], [lc, 1]],
		"wave_4": [[sc, 1], [sc, 1], [sc, 1], [mc, 2], [mc, 2], [mc, 2], [lc, 3], [lc, 3], [lc, 1]],  
		"wave_5": [[mbc, 1]],
		"wave_6": [[lc, 1], [lc, 1], [lc, 3], [mc, 1], [mc, 1], [mc, 3], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_7": [[lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 1]],
		"wave_8": [[sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 2], [lc, 1], [lc,2], [mc, 2], [lc, 1], [lc, 2], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_9": [[lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 1]],
		"wave_10": [[bbc, 1]],
	},
	"Level3": {
		"number_of_waves": 15,
		"wave_1": [[mc, 1], [mc, 1], [mc, 1], [mc, 1], [mc, 1]],
		"wave_2": [[sc, 1], [sc, 1], [sc, 1], [sc, 1], [sc, 1]],
		"wave_3": [[lc, 2], [lc, 2], [lc, 1]],
		"wave_4": [[sc, 1], [sc, 1], [sc, 1], [mc, 2], [mc, 2], [mc, 2], [lc, 3], [lc, 3], [lc, 1]],  
		"wave_5": [[mbc, 1]],
		"wave_6": [[lc, 1], [lc, 1], [lc, 3], [mc, 1], [mc, 1], [mc, 3], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_7": [[lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 1]],
		"wave_8": [[sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 2], [lc, 1], [lc,2], [mc, 2], [lc, 1], [lc, 2], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_9": [[lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 1]],
		"wave_10": [[bbc, 1]],
		"wave_11": [[sc,1],[mc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1]],
		"wave_12": [[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[mc,1],[sc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_13": [[sc,1],[sc,1],[mc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_14": [[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_15": [[mbc, 5], [bbc, 1]],
	},
	"Level4": {
		"number_of_waves": 20,
		"wave_1": [[mc, 1], [mc, 1], [mc, 1], [mc, 1], [mc, 1]],
		"wave_2": [[sc, 1], [sc, 1], [sc, 1], [sc, 1], [sc, 1]],
		"wave_3": [[lc, 2], [lc, 2], [lc, 1]],
		"wave_4": [[sc, 1], [sc, 1], [sc, 1], [mc, 2], [mc, 2], [mc, 2], [lc, 3], [lc, 3], [lc, 1]],  
		"wave_5": [[mbc, 1]],
		"wave_6": [[lc, 1], [lc, 1], [lc, 3], [mc, 1], [mc, 1], [mc, 3], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_7": [[lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 1]],
		"wave_8": [[sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 2], [lc, 1], [lc,2], [mc, 2], [lc, 1], [lc, 2], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_9": [[lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 1]],
		"wave_10": [[bbc, 1]],
		"wave_11": [[sc,1],[mc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1]],
		"wave_12": [[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[mc,1],[sc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_13": [[sc,1],[sc,1],[mc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_14": [[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_15": [[mbc, 5], [bbc, 1]],
		"wave_16": [[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1]],
		"wave_17": [[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_18": [[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1]],
		"wave_19": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1]],
		"wave_20": [[bbc, 5], [sc, 1], [sc, 1], [sc, 1], [sc, 1], [sc, 5], [mbc, 1]],
	},
	"Level5": {
		"number_of_waves": 25,
		"wave_1": [[mc, 1], [mc, 1], [mc, 1], [mc, 1], [mc, 1]],
		"wave_2": [[sc, 1], [sc, 1], [sc, 1], [sc, 1], [sc, 1]],
		"wave_3": [[lc, 2], [lc, 2], [lc, 1]],
		"wave_4": [[sc, 1], [sc, 1], [sc, 1], [mc, 2], [mc, 2], [mc, 2], [lc, 3], [lc, 3], [lc, 1]],  
		"wave_5": [[mbc, 1]],
		"wave_6": [[lc, 1], [lc, 1], [lc, 3], [mc, 1], [mc, 1], [mc, 3], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_7": [[lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 1]],
		"wave_8": [[sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 2], [lc, 1], [lc,2], [mc, 2], [lc, 1], [lc, 2], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_9": [[lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 1]],
		"wave_10": [[bbc, 1]],
		"wave_11": [[sc,1],[mc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1]],
		"wave_12": [[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[mc,1],[sc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_13": [[sc,1],[sc,1],[mc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_14": [[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_15": [[mbc, 5], [bbc, 1]],
		"wave_16": [[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1]],
		"wave_17": [[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_18": [[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1]],
		"wave_19": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1]],
		"wave_20": [[bbc, 5], [sc, 1], [sc, 1], [sc, 1], [sc, 1], [sc, 5], [mbc, 1]],
		"wave_21": [[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1]],
		"wave_22": [[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_23": [[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_24": [[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1]],
		"wave_25": [[bbc, 5], [bbc, 1]],
	},
	"Level6": {
		"number_of_waves": 30,
		"wave_1": [[mc, 1], [mc, 1], [mc, 1], [mc, 1], [mc, 1]],
		"wave_2": [[sc, 1], [sc, 1], [sc, 1], [sc, 1], [sc, 1]],
		"wave_3": [[lc, 2], [lc, 2], [lc, 1]],
		"wave_4": [[sc, 1], [sc, 1], [sc, 1], [mc, 2], [mc, 2], [mc, 2], [lc, 3], [lc, 3], [lc, 1]],  
		"wave_5": [[mbc, 1]],
		"wave_6": [[lc, 1], [lc, 1], [lc, 3], [mc, 1], [mc, 1], [mc, 3], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_7": [[lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 1]],
		"wave_8": [[sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 2], [lc, 1], [lc,2], [mc, 2], [lc, 1], [lc, 2], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_9": [[lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 1]],
		"wave_10": [[bbc, 1]],
		"wave_11": [[sc,1],[mc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1]],
		"wave_12": [[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[mc,1],[sc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_13": [[sc,1],[sc,1],[mc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_14": [[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_15": [[mbc, 5], [bbc, 1]],
		"wave_16": [[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1]],
		"wave_17": [[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_18": [[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1]],
		"wave_19": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1]],
		"wave_20": [[bbc, 5], [sc, 1], [sc, 1], [sc, 1], [sc, 1], [sc, 5], [mbc, 1]],
		"wave_21": [[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1]],
		"wave_22": [[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_23": [[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_24": [[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1]],
		"wave_25": [[bbc, 5], [bbc, 1]],
		"wave_26": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1]],
		"wave_27": [[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1]],
		"wave_28": [[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_29": [[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1]],
		"wave_30": [[bbc, 5], [mbc, 5], [bbc, 1]],
	},
	"Level7": {
		"number_of_waves": 35,
		"wave_1": [[mc, 1], [mc, 1], [mc, 1], [mc, 1], [mc, 1]],
		"wave_2": [[sc, 1], [sc, 1], [sc, 1], [sc, 1], [sc, 1]],
		"wave_3": [[lc, 2], [lc, 2], [lc, 1]],
		"wave_4": [[sc, 1], [sc, 1], [sc, 1], [mc, 2], [mc, 2], [mc, 2], [lc, 3], [lc, 3], [lc, 1]],  
		"wave_5": [[mbc, 1]],
		"wave_6": [[lc, 1], [lc, 1], [lc, 3], [mc, 1], [mc, 1], [mc, 3], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_7": [[lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 1]],
		"wave_8": [[sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 2], [lc, 1], [lc,2], [mc, 2], [lc, 1], [lc, 2], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_9": [[lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 1]],
		"wave_10": [[bbc, 1]],
		"wave_11": [[sc,1],[mc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1]],
		"wave_12": [[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[mc,1],[sc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_13": [[sc,1],[sc,1],[mc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_14": [[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_15": [[mbc, 5], [bbc, 1]],
		"wave_16": [[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1]],
		"wave_17": [[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_18": [[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1]],
		"wave_19": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1]],
		"wave_20": [[bbc, 5], [sc, 1], [sc, 1], [sc, 1], [sc, 1], [sc, 5], [mbc, 1]],
		"wave_21": [[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1]],
		"wave_22": [[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_23": [[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_24": [[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1]],
		"wave_25": [[bbc, 5], [bbc, 1]],
		"wave_26": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1]],
		"wave_27": [[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1]],
		"wave_28": [[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_29": [[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1]],
		"wave_30": [[bbc, 5], [mbc, 5], [bbc, 1]],
		"wave_31": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1]],
		"wave_32": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_33": [[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[mbc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1]],
		"wave_34": [[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1]],
		"wave_35": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[mbc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
	},
	"Level8": {
		"number_of_waves": 40,
		"wave_1": [[mc, 1], [mc, 1], [mc, 1], [mc, 1], [mc, 1]],
		"wave_2": [[sc, 1], [sc, 1], [sc, 1], [sc, 1], [sc, 1]],
		"wave_3": [[lc, 2], [lc, 2], [lc, 1]],
		"wave_4": [[sc, 1], [sc, 1], [sc, 1], [mc, 2], [mc, 2], [mc, 2], [lc, 3], [lc, 3], [lc, 1]],  
		"wave_5": [[mbc, 1]],
		"wave_6": [[lc, 1], [lc, 1], [lc, 3], [mc, 1], [mc, 1], [mc, 3], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_7": [[lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 1]],
		"wave_8": [[sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 2], [lc, 1], [lc,2], [mc, 2], [lc, 1], [lc, 2], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_9": [[lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 1]],
		"wave_10": [[bbc, 1]],
		"wave_11": [[sc,1],[mc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1]],
		"wave_12": [[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[mc,1],[sc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_13": [[sc,1],[sc,1],[mc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_14": [[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_15": [[mbc, 5], [bbc, 1]],
		"wave_16": [[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1]],
		"wave_17": [[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_18": [[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1]],
		"wave_19": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1]],
		"wave_20": [[bbc, 5], [sc, 1], [sc, 1], [sc, 1], [sc, 1], [sc, 5], [mbc, 1]],
		"wave_21": [[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1]],
		"wave_22": [[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_23": [[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_24": [[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1]],
		"wave_25": [[bbc, 5], [bbc, 1]],
		"wave_26": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1]],
		"wave_27": [[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1]],
		"wave_28": [[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_29": [[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1]],
		"wave_30": [[bbc, 5], [mbc, 5], [bbc, 1]],
		"wave_31": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1]],
		"wave_32": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_33": [[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[mbc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1]],
		"wave_34": [[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1]],
		"wave_35": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[mbc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_36": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[mbc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1]],
		"wave_37": [[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mbc,1],[sc,1],[mc,1],[sc,1]],
		"wave_38": [[sc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[sc,1],[lc,1],[mc,1],[mbc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mbc,1],[mc,1],[lc,1],[sc,1],[mc,1],[mbc,1],[bbc,1]],
		"wave_39": [[mc,1],[lc,1],[sc,1],[mbc,1],[mc,1],[lc,1],[sc,1],[mbc,1],[mc,1],[lc,1],[sc,1],[mbc,1],[mc,1],[lc,1],[sc,1],[mbc,1],[mc,1],[bbc,1],[sc,1],[mc,1]],
		"wave_40": [[lc,1],[mc,1],[sc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[sc,1],[mc,1],[bbc,1],[sc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[sc,1],[mc,1],[bbc,1]],
	},
	"Level9": {
		"number_of_waves": 45,
		"wave_1": [[mc, 1], [mc, 1], [mc, 1], [mc, 1], [mc, 1]],
		"wave_2": [[sc, 1], [sc, 1], [sc, 1], [sc, 1], [sc, 1]],
		"wave_3": [[lc, 2], [lc, 2], [lc, 1]],
		"wave_4": [[sc, 1], [sc, 1], [sc, 1], [mc, 2], [mc, 2], [mc, 2], [lc, 3], [lc, 3], [lc, 1]],  
		"wave_5": [[mbc, 1]],
		"wave_6": [[lc, 1], [lc, 1], [lc, 3], [mc, 1], [mc, 1], [mc, 3], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_7": [[lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 1]],
		"wave_8": [[sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 2], [lc, 1], [lc,2], [mc, 2], [lc, 1], [lc, 2], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_9": [[lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 1]],
		"wave_10": [[bbc, 1]],
		"wave_11": [[sc,1],[mc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1]],
		"wave_12": [[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[mc,1],[sc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_13": [[sc,1],[sc,1],[mc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_14": [[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_15": [[mbc, 5], [bbc, 1]],
		"wave_16": [[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1]],
		"wave_17": [[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_18": [[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1]],
		"wave_19": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1]],
		"wave_20": [[bbc, 5], [sc, 1], [sc, 1], [sc, 1], [sc, 1], [sc, 5], [mbc, 1]],
		"wave_21": [[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1]],
		"wave_22": [[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_23": [[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_24": [[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1]],
		"wave_25": [[bbc, 5], [bbc, 1]],
		"wave_26": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1]],
		"wave_27": [[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1]],
		"wave_28": [[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_29": [[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1]],
		"wave_30": [[bbc, 5], [mbc, 5], [bbc, 1]],
		"wave_31": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1]],
		"wave_32": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_33": [[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[mbc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1]],
		"wave_34": [[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1]],
		"wave_35": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[mbc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_36": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[mbc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1]],
		"wave_37": [[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mbc,1],[sc,1],[mc,1],[sc,1]],
		"wave_38": [[sc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[sc,1],[lc,1],[mc,1],[mbc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mbc,1],[mc,1],[lc,1],[sc,1],[mc,1],[mbc,1],[bbc,1]],
		"wave_39": [[mc,1],[lc,1],[sc,1],[mbc,1],[mc,1],[lc,1],[sc,1],[mbc,1],[mc,1],[lc,1],[sc,1],[mbc,1],[mc,1],[lc,1],[sc,1],[mbc,1],[mc,1],[bbc,1],[sc,1],[mc,1]],
		"wave_40": [[lc,1],[mc,1],[sc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[sc,1],[mc,1],[bbc,1],[sc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[sc,1],[mc,1],[bbc,1]],
		"wave_41": [[sc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[sc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[sc,1],[mc,1]],
		"wave_42": [[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[lc,1],[mc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[lc,1],[mc,1],[mbc,1],[mc,1]],
		"wave_43": [[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1]],
		"wave_44": [[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1]],
		"wave_45": [[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1]],
	},
	"Level10": {
		"number_of_waves": 50,
		"wave_1": [[mc, 1], [mc, 1], [mc, 1], [mc, 1], [mc, 1]],
		"wave_2": [[sc, 1], [sc, 1], [sc, 1], [sc, 1], [sc, 1]],
		"wave_3": [[lc, 2], [lc, 2], [lc, 1]],
		"wave_4": [[sc, 1], [sc, 1], [sc, 1], [mc, 2], [mc, 2], [mc, 2], [lc, 3], [lc, 3], [lc, 1]],  
		"wave_5": [[mbc, 1]],
		"wave_6": [[lc, 1], [lc, 1], [lc, 3], [mc, 1], [mc, 1], [mc, 3], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_7": [[lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 3], [lc, 2], [mc, 1]],
		"wave_8": [[sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 2], [lc, 1], [lc,2], [mc, 2], [lc, 1], [lc, 2], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 0.5], [sc, 1]],
		"wave_9": [[lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 0.5], [sc, 0.5], [lc, 0.5], [lc, 0.5], [lc, 1]],
		"wave_10": [[bbc, 1]],
		"wave_11": [[sc,1],[mc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1]],
		"wave_12": [[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[mc,1],[sc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_13": [[sc,1],[sc,1],[mc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_14": [[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[lc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_15": [[mbc, 5], [bbc, 1]],
		"wave_16": [[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1]],
		"wave_17": [[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_18": [[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1]],
		"wave_19": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1]],
		"wave_20": [[bbc, 5], [sc, 1], [sc, 1], [sc, 1], [sc, 1], [sc, 5], [mbc, 1]],
		"wave_21": [[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1]],
		"wave_22": [[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_23": [[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1]],
		"wave_24": [[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1]],
		"wave_25": [[bbc, 5], [bbc, 1]],
		"wave_26": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1]],
		"wave_27": [[mc,1],[sc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1]],
		"wave_28": [[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_29": [[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1]],
		"wave_30": [[bbc, 5], [mbc, 5], [bbc, 1]],
		"wave_31": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1]],
		"wave_32": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_33": [[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[mbc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1]],
		"wave_34": [[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1]],
		"wave_35": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[mbc,1],[sc,1],[lc,1],[mc,1],[sc,1],[sc,1]],
		"wave_36": [[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[mbc,1],[sc,1],[lc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1]],
		"wave_37": [[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mc,1],[sc,1],[mbc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mc,1],[sc,1],[lc,1],[mbc,1],[sc,1],[mc,1],[sc,1]],
		"wave_38": [[sc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[sc,1],[lc,1],[mc,1],[mbc,1],[sc,1],[mc,1],[lc,1],[sc,1],[mbc,1],[mc,1],[lc,1],[sc,1],[mc,1],[mbc,1],[bbc,1]],
		"wave_39": [[mc,1],[lc,1],[sc,1],[mbc,1],[mc,1],[lc,1],[sc,1],[mbc,1],[mc,1],[lc,1],[sc,1],[mbc,1],[mc,1],[lc,1],[sc,1],[mbc,1],[mc,1],[bbc,1],[sc,1],[mc,1]],
		"wave_40": [[lc,1],[mc,1],[sc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[sc,1],[mc,1],[bbc,1],[sc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[sc,1],[mc,1],[bbc,1]],
		"wave_41": [[sc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[sc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[sc,1],[mc,1]],
		"wave_42": [[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[lc,1],[mc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[lc,1],[mc,1],[mbc,1],[mc,1]],
		"wave_43": [[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1]],
		"wave_44": [[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1]],
		"wave_45": [[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1]],
		"wave_46": [[lc,1],[mbc,1],[mc,1],[bbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[mc,1],[bbc,1]],
		"wave_47": [[mbc,1],[mc,1],[bbc,1],[mbc,1],[mc,1],[lc,1],[mbc,1],[bbc,1],[mc,1],[mbc,1],[bbc,1],[mc,1],[mbc,1],[bbc,1],[mc,1],[mbc,1],[bbc,1],[mc,1],[mbc,1],[bbc,1]],
		"wave_48": [[bbc,1],[mbc,1],[mc,1],[bbc,1],[mbc,1],[lc,1],[bbc,1],[mbc,1],[mc,1],[bbc,1],[mbc,1],[mc,1],[bbc,1],[mbc,1],[mc,1],[bbc,1],[mbc,1],[mc,1],[bbc,1],[mbc,1]],
		"wave_49": [[bbc,1],[mbc,1],[bbc,1],[mbc,1],[bbc,1],[mc,1],[bbc,1],[mbc,1],[bbc,1],[mbc,1],[bbc,1],[mbc,1],[bbc,1],[mbc,1],[bbc,1],[mbc,1],[bbc,1],[mbc,1],[bbc,1],[mbc,1]],
		"wave_50": [[bbc,1],[bbc,1],[mbc,1],[bbc,1],[bbc,1],[mbc,1],[bbc,1],[bbc,1],[mbc,1],[bbc,1],[bbc,1],[mbc,1],[bbc,1],[bbc,1],[mbc,1],[bbc,1],[bbc,1],[mbc,1],[bbc,1],[bbc,1]]

	}
}
	


func reset():
	# Reset game data
	base_health = 100
	money = 850
	enemy_amount = 0
	enemy_data["medium_circle"]["health"] = 50
	enemy_data["small_circle"]["health"] = 200
	enemy_data["large_circle"]["health"] = 40
	enemy_data["mini_boss_circle"]["health"] = 1000
	enemy_data["big_boss_circle"]["health"] = 10000
