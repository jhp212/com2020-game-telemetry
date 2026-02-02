import dashboard.app as dash_app

#mimics the behaviour of requests.Response which is used by the dashboard
#neccessary because the dashboard expects responses in the same format as requests.get
class FakeResponse:
    def __init__(self, status_code=200, text="OK", json_data=None, ok=None, headers=None, json_raises=False):
        self.status_code = status_code
        self.text = text
        self._json_data = json_data

        #if 'ok' not provided, compute it using status_code
        self.ok = ok if ok is not None else (200 <= status_code < 300)

        self.headers = headers or {"content-type": "application/json"}
        self._json_raises = json_raises

    def json(self):
        if self._json_raises:
            raise ValueError("not json")
        return self._json_data



#tests if the home page renders correctly 
def test_home_render(client, monkeypatch):
    #telemetry data so the chart can be populated
    telemetry = [
        {"telemetry_type": "money_spent", "dateTime": "2026-01-01T00:00:00", "data": {"amount": 150}},
        {"telemetry_type": "enemies_destroyed", "dateTime": "2026-01-01T00:01:00", "data": {}},
    ]
    #fake api call to replace requests.get
    #neccessary so the test do not rely on real api
    def fake_get(url):
        assert url.endswith("/telemetry/")
        return FakeResponse(200, "OK", json_data=telemetry)
    #replaces requests.get only inside dashboard.app
    monkeypatch.setattr(dash_app.requests, "get", fake_get)

    #requests the home page 
    r = client.get("/")
    assert r.status_code == 200
    assert "Dashboard" in r.text  #check if Dashboard is somewhere in the page

#tests if the dashboard page renders correctly 
def test_dashboard_page_render(client, monkeypatch):
    telemetry = [
        {"telemetry_type": "money_spent", "dateTime": "2026-01-01T00:00:00", "user_id": 1, "stage_id": 1, "data": {"amount": 10}},
    ]
    #fake api response for the telemetry endpoint
    def fake_get(url):
        assert url.endswith("/telemetry/")
        return FakeResponse(200, "OK", json_data=telemetry)

    monkeypatch.setattr(dash_app.requests, "get", fake_get)

    r = client.get("/dashboard")
    assert r.status_code == 200
    #check if the heading of the page is there (may need to be changed as the template develops e.g. the heading changes)
    assert "Telemetry" in r.text

#tests that the dashboard correctly returns an error when the decision log api is unavailable 
def test_decisionlog_returns_error(client, monkeypatch):
    def fake_get(url):
        assert url.endswith("/decision_logs/")
        return FakeResponse(ok=False, status_code=503, text="backend down")

    monkeypatch.setattr(dash_app.requests, "get", fake_get)

    #requests the decision log page
    #dashboard should show the api error instead of crashing
    r = client.get("/decisionLog")
    assert r.status_code == 503
    assert "backend down" in r.text

#tests that the parameters page returns a 500 error if the api response is not valid json 
def test_parameter_returns_error(client, monkeypatch):
    #fake api response that says it was a success but returns invalid json
    def fake_get(url):
        assert url.endswith("/parameters/")
        return FakeResponse(
            status_code=200,
            text="<html>not json</html>",
            headers={"content-type": "text/html"},
            json_raises=True,   #forces .json() to raise ValueError
        )

    monkeypatch.setattr(dash_app.requests, "get", fake_get)

    #requests parameters page
    r = client.get("/parameters")
    assert r.status_code == 500
    #confirms that error handling is correct
    assert "did not return JSON" in r.text
 

#tests that the parameters page renders the table headers correctly 
def test_parameters_page_contains_table_headers(client, monkeypatch):
    params = [{"name": "enemy_damage_multiplier", "value": 1.5}]

    #fake api response for paramters endpoint
    def fake_get(url):
        assert url.endswith("/parameters/")
        return FakeResponse(200, "OK", json_data=params)


    monkeypatch.setattr(dash_app.requests, "get", fake_get)

    r = client.get("/parameters")
    assert r.status_code == 200
    #verify that the table headers that are in the template are present on the page
    assert "Parameter Name" in r.text
    assert "Value" in r.text
