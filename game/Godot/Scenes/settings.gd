extends Control

@onready var slider: HSlider = $VolumeSlider
@onready var volume_label: Label = $VolumeValueLabel
@onready var test_sound: AudioStreamPlayer = $PlacementSfx
@onready var telemetry_button: CheckButton = $TelemetryToggle

func _ready() -> void:
	slider.connect("value_changed", _on_slider_moved)
	slider.connect("drag_ended", _on_drag_ended)
	telemetry_button.connect("toggled", _on_telemetry_toggled)
	
func _on_slider_moved(value: float):
	volume_label.text = "{0}%".format([int(value*100)])

func _on_drag_ended(moved: bool):
	if moved:
		AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Master"), linear_to_db(slider.value))
		test_sound.play()

func _on_telemetry_toggled(toggled_on: bool):
	GameData.telemetry_enabled = toggled_on
	telemetry_button.text = "ON" if toggled_on else "OFF"
