extends Node

# Money
var money := 550

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
		"damage": 30,
		"rof": 1,
		"range": 250,
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
		"speed": 90,
		"cash": 100,
		"damage": 2
	},
	"large_circle": {
		"health": 100,
		"speed": 60,
		"cash": 250,
		"damage": 5
	},
	"small_circle": {
		"health": 40,
		"speed": 110,
		"cash": 80,
		"damage": 1
	}
}
