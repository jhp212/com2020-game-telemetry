extends Node

var base_url: String = ""

var username: String
var password: String

var JWT: String
var user_id: int

func get_http_request() -> HTTPRequest:
	var http_request = HTTPRequest.new()
	add_child(http_request)
	return http_request

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

func _ready() -> void:
	_initialize_url()
	
func register(username_input: String, password_input: String):
	var url = get_full_url("/auth/register")
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"username": username_input, "password": password_input})
	
	var http_request = get_http_request()
	http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	
	# Wait for the server to reply
	var result = await http_request.request_completed
	http_request.queue_free()
	
	var response_code = result[1]
	var response_body = result[3].get_string_from_utf8()
	
	if response_code == 200 or response_code == 201:
		return "OK"
	elif response_code == 400:
		return "EXISTS"
	else:
		return "ERR"

func authenticate(username_input: String, password_input: String):
	var url = get_full_url("/auth/token")

	var headers = ["Content-Type: application/x-www-form-urlencoded"]
	var body = "username=" + username_input.uri_encode() + "&password=" + password_input.uri_encode()
	
	var http_request = get_http_request()
	http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	
	var result = await http_request.request_completed
	http_request.queue_free()
	
	var response_code = result[1]
	var response_body = result[3].get_string_from_utf8()
	
	if response_code == 200:
		var parsed_response = JSON.parse_string(response_body)
		JWT = parsed_response.get("access_token")
		user_id = parsed_response.get("user_id")
		username = username_input
		password = password_input
		return "OK"
	elif response_code == 401:
		return "WRONG"
	else:
		return "ERR"

func logout():
	username = ""
	password = ""
	JWT = ""
	user_id = -1

func delete_account():
	if not JWT:
		print("Not Logged In")
		if username and password:
			await authenticate(username, password)
	
	var url = get_full_url("/auth/delete_account")
	var headers = [
		"Content-Type: application/json",
		"Authorization: Bearer " + JWT
	]
	var http_request = get_http_request()
	var error = http_request.request(url, headers, HTTPClient.METHOD_DELETE)

	if error != OK:
		print("Error making request to: " + url)
		http_request.queue_free() # Clean up early exit
		return null
	
	var result = await http_request.request_completed
	http_request.queue_free()

	var response_code = result[1]
	var response_body = result[3].get_string_from_utf8()

	if response_code == 200:
		logout() # Clear local credentials on successful deletion
		return "OK"
	elif response_code == 401:
		print("Unauthorized. Refreshing token and retrying...")
		if username and password:
			await authenticate(username, password)
			return await delete_account()
		return null
	else:
		print("Delete Account Error ", response_code, ": ", response_body)
		return "ERR"
		
func create_telemetry(telemetry_data):
	# Send telemetry data to the database
	if not JWT:
		print("Not Logged In")
		if username and password:
			await authenticate(username, password)
			
	var json_data = JSON.stringify(telemetry_data)
	var headers = [
		"Content-Type: application/json",
		"Authorization: Bearer " + JWT
	]
	var url = get_full_url("/telemetry")
	var http_request = get_http_request()
	var error := http_request.request(url, headers, HTTPClient.METHOD_POST, json_data)
	
	if error != OK:
		print("Error making request to: " + url)
		http_request.queue_free() # Clean up early exit
		return null
		
	var result = await http_request.request_completed
	http_request.queue_free()
	
	var response_code = result[1]
	var response_body = result[3].get_string_from_utf8()
	
	if response_code == 401: 
		print("Unauthorized. Refreshing token and retrying...")
		if username and password:
			await authenticate(username, password)
			return await create_telemetry(telemetry_data)
		return null
		
	if response_code == 200 or response_code == 201:
		return JSON.parse_string(response_body)
	else:
		print("Telemetry Error ", response_code, ": ", response_body)
		return null

func get_parameter(parameter_name, default_value := 1.0):
	# Acquire parameter from the database
	if not JWT:
		print("Not Logged In")
		if username and password:
			await authenticate(username, password) # FIX: Properly await async function
		
	var headers = [
		"Content-Type: application/json",
		"Authorization: Bearer " + JWT
	]
	var url = get_full_url("/parameters?parameter_name=" + parameter_name)
	var http_request = get_http_request()
	var error = http_request.request(url, headers, HTTPClient.METHOD_GET)
	
	if error != OK:
		print("Error making request to: " + url)
		http_request.queue_free() # Clean up early exit
		return default_value
		
	var result = await http_request.request_completed
	http_request.queue_free()
	
	var response_code = result[1]
	var response_body = result[3].get_string_from_utf8()
	
	if response_code == 401:
		print("Unauthorized. Refreshing token and retrying...")
		if username and password:
			await authenticate(username, password)
			return await get_parameter(parameter_name)
		return default_value
		
	if response_code == 200:
		return JSON.parse_string(response_body)
	else:
		print("Parameter Error ", response_code, ": ", response_body)
		return default_value
	
func log_event(event_type: String, payload := {}):
	# Create a telemetry event
	var telemetry_data := {
		"user_id": user_id, 
		"stage_id": GameData.current_stage,
		"telemetry_type": event_type,
		"dateTime": Time.get_datetime_string_from_system(),
		"data": payload
	}
	print("telemetry logging")
	await create_telemetry(telemetry_data)
