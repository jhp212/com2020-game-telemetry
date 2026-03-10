extends Control

@onready var username_line: LineEdit = $Border/VBoxContainer/UsernameLine
@onready var password_line: LineEdit = $Border/VBoxContainer/PasswordLine
@onready var message: Label = $Border/VBoxContainer/MarginContainer2/Message


func _on_login_button_pressed() -> void:
	var username = username_line.text
	var password = password_line.text
	
	var data = {"username": username, "password": password}
	
	## Send Post request

func on_post_request_complete(result):
	pass
	
	# Login ok, switch to main menu
	#if result["status"] == "success":
		#get_trree().change_scene_to_file("res://Scenes/scene_handler.tscn")
	
	# No result
	#if result == null:
		# message_label.text = "Server error. Try again."
	
	# Login failed
	#else:
		# message_label.text = "Invalid username or password! Try again."
