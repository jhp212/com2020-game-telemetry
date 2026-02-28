from datetime import datetime, timezone

#this tests if the dashboard is successfully accessing and displaying the telemtry events  
def test_telemetry_page(auth_db_client, dashboard_client):
    #using api to create a telemetry event in the database
    #later tests test if it is accessible from the dashboard 
    payload = {
        "user_id": 12345,  #using a number that is unlikely to show in the html 
        "stage_id": 6789, #using a number that is unlikely to show in the html  
        "telemetry_type": "money_spent",
        "dateTime": datetime.now(timezone.utc).isoformat(),
        "data": {"amount": 125, "total_remaining": 425},
    }
    #sending it to the db
    r = auth_db_client.post("/telemetry/", json=payload)
    assert r.status_code == 200, r.text #checking if it was successful 

    #load dashboard page which should load the telemntry page 
    page = dashboard_client.get("/dashboard")
    assert page.status_code == 200

    #this checks that the data is somewhere in the html
    #which confirms that the dashboard is successfully accessing and displaying the data from the db
    assert "money_spent" in page.text
    assert "12345" in page.text
    assert "6789" in page.text
    assert "125" in page.text  # amount

#this tests if the dashboard is successfully accessing and displaying the parameters
def test_parameters_page(auth_db_client, dashboard_client):
    #creating parameter using db API again
    r = auth_db_client.post("/parameters/", json={"name": "enemy_damage_multiplier", "value": 1.5})
    assert r.status_code == 200, r.text #check if successful 

    #loading the parameters page on the dashboard 
    page = dashboard_client.get("/parameters")
    assert page.status_code == 200 #check request was successful  

    assert "enemy_damage_multiplier" in page.text
    assert "1.5" in page.text

#this tests if the dashboard is successfully accessing and displaying the parameters
def test_decisionlog_page(auth_db_client, dashboard_client):
    #creating a parameter since decision log requires one to exist first 
    r = auth_db_client.post("/parameters/", json={"name": "enemy1_health", "value": 5.0})
    assert r.status_code == 200, r.text
    
    #creating the decision log entry 
    r = auth_db_client.post("/decision_logs/", json={
        "parameter_name": "enemy1_health",
        "stage_id": 1,
        "change": "-2",
        "rationale": "enemy is too strong",
        "evidence": "test evidence",
        "dateTime": datetime.now(timezone.utc).isoformat(),
    })
    assert r.status_code == 200, r.text

    #loading the decision log page
    page = dashboard_client.get("/decisionLog")
    assert page.status_code == 200
    
    #checks that the data is somewhere in the html
    assert "enemy1_health" in page.text
    assert "-2" in page.text
    assert "enemy is too strong" in page.text
