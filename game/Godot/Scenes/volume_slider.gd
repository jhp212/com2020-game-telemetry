extends Control

@onready var slider: HSlider = $VolumeSlider
@onready var volume_label: Label = $VolumeValueLabel
@onready var test_sound: AudioStreamPlayer = $PlacementSfx

func _ready() -> void:
	slider.connect("value_changed", _on_slider_moved)
	slider.connect("drag_ended", _on_drag_ended)
	
func _on_slider_moved(value: float):
	volume_label.text = "{0}%".format([int(value*100)])

func _on_drag_ended(moved: bool):
	if moved:
		GameData.volume = slider.value*100
		AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Master"), linear_to_db(slider.value))
		test_sound.play()
