extends Panel

signal upgrade(current_tower)
signal sell(sold_tower)

var current_tower
var sold

func set_tower(tower):
	if tower == sold:
		$VBoxContainer/TowerName.text = ""
		$VBoxContainer/HBoxContainer/TowerImage.texture = StyleBoxEmpty
		$VBoxContainer/HBoxContainer/Panel/MarginContainer/VBoxContainer/HBoxContainer/Upgrade1.disabled = true
		$VBoxContainer/HBoxContainer/Panel/MarginContainer/VBoxContainer/HBoxContainer/Upgrade1.text = ""
		$VBoxContainer/HBoxContainer/Panel/MarginContainer/VBoxContainer/HBoxContainer/Description1.text = ""
	else:
		current_tower = tower
		print(current_tower.name)
		var ttype = current_tower.tower_type
		var stage = GameData.tower_upgrades[current_tower.tower_type]["stage"]
		$VBoxContainer/HBoxContainer/TowerImage.texture = load("res://Assets/Towers/" + ttype + ".png")
		$VBoxContainer/TowerName.text = ttype
		if stage == 3:
			$VBoxContainer/HBoxContainer/Panel/MarginContainer/VBoxContainer/HBoxContainer/Upgrade1.disabled = true
			$VBoxContainer/HBoxContainer/Panel/MarginContainer/VBoxContainer/HBoxContainer/Upgrade1.text = "Fully Upgraded!"
			$VBoxContainer/HBoxContainer/Panel/MarginContainer/VBoxContainer/HBoxContainer/Description1.text = "Fully Upgraded!"
		else:
			$VBoxContainer/HBoxContainer/Panel/MarginContainer/VBoxContainer/HBoxContainer/Upgrade1.disabled = false
			$VBoxContainer/HBoxContainer/Panel/MarginContainer/VBoxContainer/HBoxContainer/Upgrade1.text = GameData.tower_upgrades[ttype]["1"]
			$VBoxContainer/HBoxContainer/Panel/MarginContainer/VBoxContainer/HBoxContainer/Description1.text = GameData.tower_upgrades[ttype]["1desc"]


func _on_upgrade_1_pressed() -> void:
	print("llllllllll")
	upgrade.emit(current_tower)

func _on_sell_button_pressed() -> void:
	set_tower(sold)
	sell.emit(current_tower)

var shown = false

func _on_move_button_pressed() -> void:
	if shown:
		$"../AnimationPlayer".play("tower_panel_down")
		shown = false
	elif shown == false:
		$"../AnimationPlayer".play("tower_panel_up")
		shown = true
