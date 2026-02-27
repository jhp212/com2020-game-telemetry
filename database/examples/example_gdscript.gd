extends Node

var base_url = "http://127.0.0.1:10101"
var http_request: HTTPRequest

func _ready():
    # Dynamically create an HTTPRequest node to handle the network calls
    http_request = HTTPRequest.new()
    add_child(http_request)
    
    await run_example_flow()

func run_example_flow():
    var username = "testuser"
    var password = "testpassword"
    
    # --- 1. Register a new user ---
    print("Registering user...")
    var reg_response = await register(username, password)
    if not reg_response.is_empty():
        print("User registered successfully: ", reg_response)
    else:
        print("Registration failed (or user already exists).")

    # --- 2. Authenticate and get access token ---
    print("\nAuthenticating...")
    var auth_response = await authenticate(username, password)
    if auth_response.is_empty():
        print("Authentication failed.")
        return
        
    var token = auth_response.get("access_token")
    var user_id = auth_response.get("user_id")
    
    print("Access token: ", token)
    print("User ID: ", user_id)

    # --- 3. Create a new telemetry entry ---
    var telemetry_data = {
        "user_id": user_id,
        "telemetry_type": "stage_start",
        "stage_id": 1,
        "data": {},
        "dateTime": Time.get_datetime_string_from_system(true) 
    }
    
    print("\nSending telemetry...")
    var tel_response = await create_telemetry(token, telemetry_data)
    if not tel_response.is_empty():
        print("Telemetry entry created: ", tel_response)

# --- API Call Functions ---

func register(username: String, password: String) -> Dictionary:
    var url = base_url + "/auth/register"
    var headers = ["Content-Type: application/json"]
    var body = JSON.stringify({"username": username, "password": password})
    
    http_request.request(url, headers, HTTPClient.METHOD_POST, body)
    
    # Wait for the server to reply
    var result = await http_request.request_completed
    var response_code = result[1]
    var response_body = result[3].get_string_from_utf8()
    
    if response_code == 200:
        return JSON.parse_string(response_body)
    else:
        print("Register Error ", response_code, ": ", response_body)
        return {}

func authenticate(username: String, password: String) -> Dictionary:
    var url = base_url + "/auth/token"
    # Crucial: OAuth2 requires form-urlencoded data for login!
    var headers = ["Content-Type: application/x-www-form-urlencoded"]
    var body = "username=" + username.uri_encode() + "&password=" + password.uri_encode()
    
    http_request.request(url, headers, HTTPClient.METHOD_POST, body)
    
    var result = await http_request.request_completed
    var response_code = result[1]
    var response_body = result[3].get_string_from_utf8()
    
    if response_code == 200:
        return JSON.parse_string(response_body)
    else:
        print("Auth Error ", response_code, ": ", response_body)
        return {}

func create_telemetry(token: String, telemetry_data: Dictionary) -> Dictionary:
    var url = base_url + "/telemetry"
    # Attach our Bearer token to the headers
    var headers = [
        "Content-Type: application/json",
        "Authorization: Bearer " + token
    ]
    var body = JSON.stringify(telemetry_data)
    
    http_request.request(url, headers, HTTPClient.METHOD_POST, body)
    
    var result = await http_request.request_completed
    var response_code = result[1]
    var response_body = result[3].get_string_from_utf8()
    
    if response_code == 200:
        return JSON.parse_string(response_body)
    else:
        print("Telemetry Error ", response_code, ": ", response_body)
        return {}