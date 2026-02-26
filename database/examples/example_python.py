import requests, datetime

BASE_URL = "http://127.0.0.1:10101"

# --- AUTHENTICATION ---
def register(username: str, password: str):
    response = requests.post(f"{BASE_URL}/auth/register", json={"username": username, "password": password})
    if response.status_code != 200:
        raise Exception(f"Registration failed: {response.text}")
    return response.json()

def authenticate(username: str, password: str):
    response = requests.post(f"{BASE_URL}/auth/token", data={"username": username, "password": password})
    if response.status_code != 200:
        raise Exception(f"Authentication failed: {response.text}")
    data = response.json()
    access_token = data.get("access_token")
    user_id = data.get("user_id")
    if not access_token:
        raise Exception("No access token returned")
    return access_token, user_id

def create_telemetry(token: str, telemetry_data: dict):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/telemetry/", json=telemetry_data, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to create telemetry: {response.text}")
    return response.json()

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    # Register a new user
    try:
        register("testuser", "testpassword")
        print("User registered successfully")
    except Exception as e:
        print(e)

    # Authenticate and get access token
    try:
        token, user_id = authenticate("testuser", "testpassword")
        print(f"Access token: {token}")
        print(f"User ID: {user_id}")
        if not token:
            raise Exception("Authentication failed: No token received")
        if not user_id:
            raise Exception("Authentication failed: No user ID received")
    except Exception as e:
        print(e)

    # Create a new telemetry entry
    telemetry_data = {
        "user_id": user_id, # type: ignore
        "telemetry_type": "stage_start",
        "stage_id": 1,
        "data": {},
        "dateTime": datetime.datetime.now().isoformat()
    }

    try:
        telemetry_entry = create_telemetry(token, telemetry_data) # type: ignore
        print("Telemetry entry created:", telemetry_entry)
    except Exception as e:
        print(e)