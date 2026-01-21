import requests, json

BASE_URL = "http://127.0.0.1:8000"

def create_telemetry(telemetry_data):
    response = requests.post(f"{BASE_URL}/telemetry/", json=telemetry_data)
    return response.json()

def get_all_telemetry():
    response = requests.get(f"{BASE_URL}/telemetry/")
    return response.json()

def create_parameter(parameter_data):
    response = requests.post(f"{BASE_URL}/parameters/", json=parameter_data)
    return response.json()

def get_all_parameters():
    response = requests.get(f"{BASE_URL}/parameters/")
    return response.json()

if __name__ == "__main__":
    # Example telemetry data
    telemetry_data = {
        "user_id": 1,
        "stage_id": 2,
        "telemetry_type": "money_spent",
        "dateTime": "2026-01-21T17:38:00",
        "data": {"amount": 150, "total_remaining": 850}
    }

    # Create a new telemetry record
    created_telemetry = create_telemetry(telemetry_data)
    print("Created Telemetry:", json.dumps(created_telemetry, indent=2))

    # Get all telemetry records
    all_telemetry = get_all_telemetry()
    print("All Telemetry Records:", json.dumps(all_telemetry, indent=2))

    parameter_data = {
        "name": "enemy_damage_multiplier",
        "value": 1.5
    }

    # Create a new parameter record
    created_parameter = create_parameter(parameter_data)
    print("Created Parameter:", json.dumps(created_parameter, indent=2))

    # Get all parameter records
    all_parameters = get_all_parameters()
    print("All Parameter Records:", json.dumps(all_parameters, indent=2))

    # Update the parameter value
    parameter_data["value"] = 2.0
    created_parameter = create_parameter(parameter_data)
    print("Updated Parameter:", json.dumps(created_parameter, indent=2))