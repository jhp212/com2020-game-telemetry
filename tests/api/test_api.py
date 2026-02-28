from datetime import datetime, timezone

#tests adding a balancing rule to the db 
def test_balancing_rule(auth_client):
    created = auth_client.post("/balancing_rules/", json={
        "trigger_condition": "time_alive < 10",
        "suggested_change": "increase_damage",
        "explanation": "increase damage of towers in aims of increasing play time "
    }).json()

    r = auth_client.get(f"/balancing_rules/?rule_id={created['id']}")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 1
    assert rows[0]["trigger_condition"] == "time_alive < 10"

#tests creating an entry into the decision log 
def test_create_decision_log(auth_client):
    #first add a parameter to the DB, since decision log requires a parameter to exist
    auth_client.post("/parameters/", json={"name": "enemy1_health", "value": 5.0})
    r = auth_client.post("/decision_logs/", json={
        "parameter_name": "enemy1_health", "stage_id": 1, "change": "-2",
        "rationale": "enemy is too strong", "evidence": 'very convincing evidence',
        "dateTime": datetime.now(timezone.utc).isoformat(),
    })
    assert r.status_code == 200
    assert r.json()["parameter_name"] == "enemy1_health"

#tests filtering decision log based on parameter
#create two entries for different parameters, checks if there is only one row after filtering 
def test_filter_decision_logs(auth_client):
    auth_client.post("/parameters/", json={"name": "enemy1_health", "value": 3.0})
    auth_client.post("/parameters/", json={"name": "enemy_damage_multiplier", "value": 1.5})

    now = datetime.now(timezone.utc).isoformat()
    auth_client.post("/decision_logs/", json={
        "parameter_name": "enemy1_health", "stage_id": 1, "change": "-1",
        "rationale": "still too strong", "evidence": 'slightly less convincing evidence', "dateTime": now
    })
    auth_client.post("/decision_logs/", json={
        "parameter_name": "enemy_damage_multiplier", "stage_id": 1, "change": "1.25",
        "rationale": "way too much damage", "evidence": 'good evidence', "dateTime": now
    })

    r = auth_client.get("/decision_logs/?parameter_name=enemy_damage_multiplier")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 1
    assert rows[0]["parameter_name"] == "enemy_damage_multiplier"

#tests creating a parameter
def test_create_parameter(auth_client):
    r = auth_client.post("/parameters/", json={"name": "enemy1_health", "value": 5.0})
    assert r.status_code == 200
    assert r.json()["value"] == 5.0

#tests updating an existing parameter 
def test_update_parameter(auth_client):
    auth_client.post("/parameters/", json={"name": "enemy1_health", "value": 5.0})
    r = auth_client.post("/parameters/", json={"name": "enemy1_health", "value": 2.0})
    assert r.status_code == 200
    assert r.json()["value"] == 2.0

#tests filtering parameters by their name 
def test_filter_parameters(auth_client):
    auth_client.post("/parameters/", json={"name": "enemy1_health", "value": 1.0})
    auth_client.post("/parameters/", json={"name": "enemy_damage_multiplier", "value": 1.5})

    r = auth_client.get("/parameters/?parameter_name=enemy_damage_multiplier")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 1
    assert rows[0]["name"] == "enemy_damage_multiplier"


#tests creating a telemtary event entry
def test_create_telemetry(auth_client):
    now = datetime.now(timezone.utc)
    r = auth_client.post("/telemetry/", json={
        "user_id": 1,
        "stage_id": 1,
        "telemetry_type": "tower_spawn",
        "dateTime": now.isoformat(),
        "data": {"amount": 150, "tower_spawn": 5},
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["user_id"] == 1
    assert body["data"]["amount"] == 150
    assert body["data"]["tower_spawn"] == 5

#tests filitering telemetry events by user id 
def test_filter_telemetry(auth_client):
    now = datetime.now(timezone.utc).isoformat()

    auth_client.post("/telemetry/", json={
        "user_id": 2, "stage_id": 1, "telemetry_type": "enemy_defeated",
        "dateTime": now, "data": {}
    })
    auth_client.post("/telemetry/", json={
        "user_id": 3, "stage_id": 1, "telemetry_type": "money_spent",
        "dateTime": now, "data": {}
    })

    r = auth_client.get("/telemetry/", params={"user_id": 2})
    assert r.status_code == 200, r.text
    rows = r.json()
    assert len(rows) == 1
    assert rows[0]["user_id"] == 2

