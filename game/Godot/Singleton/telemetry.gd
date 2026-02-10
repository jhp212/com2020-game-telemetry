extends Node

const BASE_URL = "http://127.0.0.1:10101"

func create_telemetry(telemetry_data):
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


func log_event(event_type: String, payload := {}):
	var telemetry_data := {
		"user_id": GameData.user_id,
		"stage_id": GameData.current_stage,
		"telemetry_type": event_type,
		"dateTime": Time.get_datetime_string_from_system(),
		"data": payload
	}
	await create_telemetry(telemetry_data)
