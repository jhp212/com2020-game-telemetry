extends Node

const BASE_URL = "http://127.0.0.1:8000"

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

func get_all_telemetry():
    var http_request = HTTPRequest.new()
    add_child(http_request)
    var error = http_request.request(BASE_URL + "/telemetry/", [], HTTPClient.METHOD_GET)
    if error != OK:
        print("Error making request")
        return null
    var result = await http_request.request_completed
    var response_body = result[3]
    var json = JSON.new()
    json.parse(response_body.get_string_from_utf8())
    http_request.queue_free()
    return json.get_data()

func create_parameter(parameter_data):
    var http_request = HTTPRequest.new()
    add_child(http_request)
    var json_data = JSON.stringify(parameter_data)
    var headers = ["Content-Type: application/json"]
    var error = http_request.request(BASE_URL + "/parameters/", headers, HTTPClient.METHOD_POST, json_data)
    if error != OK:
        print("Error making request")
        return null
    var result = await http_request.request_completed
    var response_body = result[3]
    var json = JSON.new()
    json.parse(response_body.get_string_from_utf8())
    http_request.queue_free()
    return json.get_data()

func get_all_parameters():
    var http_request = HTTPRequest.new()
    add_child(http_request)
    var error = http_request.request(BASE_URL + "/parameters/", [], HTTPClient.METHOD_GET)
    if error != OK:
        print("Error making request")
        return null
    var result = await http_request.request_completed
    var response_body = result[3]
    var json = JSON.new()
    json.parse(response_body.get_string_from_utf8())
    http_request.queue_free()
    return json.get_data()

func _ready():
    # Example telemetry data
    var telemetry_data = {
        "user_id": 1,
        "stage_id": 2,
        "telemetry_type": "money_spent",
        "dateTime": "2026-01-21T17:38:00",
        "data": {"amount": 150, "total_remaining": 850}
    }

    # Create a new telemetry record
    var created_telemetry = await create_telemetry(telemetry_data)
    print("Created Telemetry: ", JSON.stringify(created_telemetry, "\t"))

    # Get all telemetry records
    var all_telemetry = await get_all_telemetry()
    print("All Telemetry Records: ", JSON.stringify(all_telemetry, "\t"))

    var parameter_data = {
        "name": "enemy_damage_multiplier",
        "value": 1.5
    }

    # Create a new parameter record
    var created_parameter = await create_parameter(parameter_data)
    print("Created Parameter: ", JSON.stringify(created_parameter, "\t"))

    # Get all parameter records
    var all_parameters = await get_all_parameters()
    print("All Parameter Records: ", JSON.stringify(all_parameters, "\t"))

    # Update the parameter value
    parameter_data["value"] = 2.0
    created_parameter = await create_parameter(parameter_data)
    print("Updated Parameter: ", JSON.stringify(created_parameter, "\t"))