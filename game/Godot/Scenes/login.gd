extends Control

@onready var username_line: LineEdit = $LoginScreen/VBoxContainer/UsernameLine
@onready var password_line: LineEdit = $LoginScreen/VBoxContainer/PasswordLine
@onready var message: Label = $LoginScreen/VBoxContainer/MarginContainer2/Message


func _on_login_button_pressed() -> void:
	var username = username_line.text
	var password = password_line.text
	
	if username.length() < 1:
		message.text = "Please enter a username!"
		return
	if password.length() < 1:
		message.text = "Please enter a password!"
		return
		
	var result = await Telemetry.authenticate(username, password)
	
	if result == "OK":
		GameData.update_data()
		get_tree().change_scene_to_file("res://Scenes/scene_handler.tscn")
	elif result == "WRONG":
		message.text = "Username or Password is incorrect"
		password_line.text = ""
	elif result == "ERR":
		message.text = "Server Error, please try again later"

func _on_register_button_pressed() -> void:
	var username = username_line.text
	var password = password_line.text
	
	if username.length() < 1:
		message.text = "Please enter a username!"
		return
	if password.length() < 1:
		message.text = "Please enter a password!"
		return
		
	var result = await Telemetry.register(username, password)
	
	if result == "OK":
		message.text = "Registered Successfully! Please log in"
	elif result == "EXISTS":
		message.text = "Username already taken."
	elif result == "ERR":
		message.text = "Server Error, please try again later"
