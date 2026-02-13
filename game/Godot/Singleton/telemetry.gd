extends Node

# Default to local dev server, but override for HTML5 (browser) exports
const DEFAULT_BASE_URL = "http://127.0.0.1:10101"
var BASE_URL = DEFAULT_BASE_URL

func _ready():
	# When running as an HTML5 export (in-browser), use same-origin relative URLs
	if OS.has_feature("HTML5"):
		BASE_URL = ""

func create_telemetry(telemetry_data):
	# Send telemtry data to the database
	var http_request = HTTPRequest.new()
	add_child(http_request)
	var json_data = JSON.stringify(telemetry_data)
	var headers = ["Content-Type: application/json"]
	var error = http_request.request(BASE_URL + "/telemetry/", headers, HTTPClient.METHOD_POST, json_data)
	if error != OK:
		print("Error making request")
		return null
	var result = await http_request.request_completed
	var response_body = result[3]
	var json = JSON.new()
	json.parse(response_body.get_string_from_utf8())
	http_request.queue_free()
	return json.get_data()

func get_parameter(parameter_name):
	# Aquire parameter from the database
	var http_request = HTTPRequest.new()
	add_child(http_request)
	var headers = ["Content-Type: application/json"]
	var error = http_request.request(BASE_URL + "/parameters/?parameter_name=" + parameter_name, headers, HTTPClient.METHOD_GET)
	if error != OK:
		print("Error making request")
		return null
	var result = await http_request.request_completed
	var response_body = result[3]
	var json = JSON.new()
	json.parse(response_body.get_string_from_utf8())
	http_request.queue_free()
	return json.get_data()
	
func log_event(event_type: String, payload := {}):
	# Create a telemetry event
	var telemetry_data := {
		"user_id": GameData.user_id,
		"stage_id": GameData.current_stage,
		"telemetry_type": event_type,
		"dateTime": Time.get_datetime_string_from_system(),
		"data": payload
	}
	await create_telemetry(telemetry_data)
