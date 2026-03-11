extends Control

func _ready() -> void:
	$LogoutButton.connect("pressed", _on_logout_button_pressed)
	var username = Telemetry.username
	$Username.text += username

func _on_logout_button_pressed():
	Telemetry.logout()
	get_tree().change_scene_to_file("res://Scenes/login.tscn")
