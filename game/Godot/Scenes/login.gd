extends Control

@onready var username_line: LineEdit = $LoginScreen/VBoxContainer/UsernameLine
@onready var password_line: LineEdit = $LoginScreen/VBoxContainer/PasswordLine
@onready var message: Label = $LoginScreen/VBoxContainer/MarginContainer2/Message

func _is_valid_username(username: String) -> bool:
	if username.length() < 3 or username.length() > 20:
		return false
	for c in username:
		if not (c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"):
			return false
	return true

func _is_valid_password(password: String) -> bool:
	if password.length() < 8:
		return false
	var has_upper = false
	var has_lower = false
	var has_digit = false
	var has_special = false
	for c in password:
		if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
			has_upper = true
		elif c in "abcdefghijklmnopqrstuvwxyz":
			has_lower = true
		elif c in "0123456789":
			has_digit = true
		elif c in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/\\":
			has_special = true
	return has_upper and has_lower and has_digit and has_special

func _on_login_button_pressed() -> void:
	var username = username_line.text
	var password = password_line.text
	
	if not _is_valid_username(username):
		message.text = "Username must be between 3 and 20 characters long and contain only letters, numbers, and underscores!"
		return
		
	if not _is_valid_password(password):
		message.text = "Password must be at least 8 characters long and include uppercase, lowercase, digit, and special character!"
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
	
	if not _is_valid_username(username):
		message.text = "Username must be between 3 and 20 characters long and contain only letters, numbers, and underscores!"
		return
	if not _is_valid_password(password):
		message.text = "Password must be at least 8 characters long and include uppercase, lowercase, digit, and special character!"
		return
		
	var result = await Telemetry.register(username, password)
	
	if result == "OK":
		message.text = "Registered Successfully! Please log in"
	elif result == "EXISTS":
		message.text = "Username already taken."
	elif result == "ERR":
		message.text = "Server Error, please try again later"
