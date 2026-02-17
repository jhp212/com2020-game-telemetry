extends Node

var base_url: String = ""

func _initialize_url():
	# Get the full URL from the browser's current location
	# This works in web exports by using JavaScript interop
	if base_url != "":
		return  # Already initialized
	
	if OS.get_name() == "Web":
		base_url = JavaScriptBridge.eval("window.location.origin")
		print("Web export - using origin: " + base_url)
	else:
		base_url = "http://localhost:10103"
		print("Desktop/Editor - using: " + base_url)

func get_full_url(path: String) -> String:
	_initialize_url()  # Ensure URL is set before use
	if base_url == "":
		print("ERROR: Failed to initialize base_url")
		return ""
	return base_url + "/api" + path

func create_telemetry(telemetry_data):
	# Send telemtry data to the database
	var http_request = HTTPRequest.new()
	add_child(http_request)
	var json_data = JSON.stringify(telemetry_data)
	var headers = ["Content-Type: application/json"]
	var url = get_full_url("/telemetry/")
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, json_data)
	if error != OK:
		print("Error making request to: " + url)
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
	var url = get_full_url("/parameters/?parameter_name=" + parameter_name)
	var error = http_request.request(url, headers, HTTPClient.METHOD_GET)
	if error != OK:
		print("Error making request to: " + url)
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
