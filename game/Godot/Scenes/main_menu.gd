extends Control

var settings_visible := false
var confirmed_clicks := 0

func _ready() -> void:
	$LogoutButton.connect("pressed", _on_logout_button_pressed)
	var username = Telemetry.username
	$Username.text += username
	$Cog.connect("clicked", _toggle_settings_menu)
	$SettingsMenu/DeleteDataButton.connect("pressed", _on_delete_data_button_pressed)

func _on_logout_button_pressed():
	Telemetry.logout()
	get_tree().change_scene_to_file("res://Scenes/login.tscn")

func _toggle_settings_menu():
	$LevelSelect.visible  = not $LevelSelect.visible
	$HowToPlay.visible    = false
	$SettingsMenu.visible = not $SettingsMenu.visible

func _on_delete_data_button_pressed():
	if confirmed_clicks == 0:
		$SettingsMenu/DeleteDataButton.text = "Are you sure? This will delete your account and all associated data."
		confirmed_clicks+=1
	elif confirmed_clicks == 1:
		var result = await Telemetry.delete_account()
		if result == "OK":
			confirmed_clicks = 0
			get_tree().change_scene_to_file("res://Scenes/login.tscn")




func _on_htp_button_pressed() -> void:
	$HowToPlay.visible = not $HowToPlay.visible
