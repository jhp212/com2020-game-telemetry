extends Node

# Player Health
var base_health = 100
signal base_health_changed(new_health)

func damage_base(amount):
	base_health -= amount
	base_health = max(base_health, 0)
	base_health_changed.emit(base_health)

# Money
var money := 850
signal money_changed(new_amount)

func can_afford(amount):
	return money >= amount

func spend(amount):
	if not can_afford(amount):
		print("Not enough money")
		return false

	money -= amount
	money_changed.emit(money)
	return true

func add_money(amount):
	money += amount
	money_changed.emit(money)
	print(money)

# Tower Data
var tower_data = {
	"triangle_stock": {
		"damage": 20,
		"rof": 2,
		"range": 350,
		"cost": 250},
	"square_stock": {
		"damage": 35,
		"rof": 1,
		"range": 10000,
		"cost": 550},
	"star_stock": {
		"damage": 10,
		"rof": 3,
		"range": 350,
		"cost": 450}
	}

# Enemy Data
var enemy_data = {
	"medium_circle": {
		"health": 50,
		"speed": 200,
		"cash": 100,
		"damage": 2
	},
	"large_circle": {
		"health": 150,
		"speed": 30,
		"cash": 250,
		"damage": 5
	},
	"small_circle": {
		"health": 40,
		"speed": 80,
		"cash": 80,
		"damage": 1
	}
}
