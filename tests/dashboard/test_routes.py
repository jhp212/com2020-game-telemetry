import dashboard.app as dash_app


#simualtes a requests.Response object so no real http calls are made 
class FakeResponse:
    def __init__(self, status_code=200, text="OK", json_data=None, ok=None, headers=None, json_raises=False):
        self.status_code = status_code
        self.text = text
        self._json_data = json_data
        #determines if ok is not provided 
        self.ok = ok if ok is not None else (200 <= status_code < 300)
        #default response type is json
        self.headers = headers or {"content-type": "application/json"}
        self._json_raises = json_raises

    def json(self):
        #simulates invalid json response if needed 
        if self._json_raises:
            raise ValueError("not json")
        return self._json_data


#dahsboard calls requests>post(url+/auth/token)
#this replaces the call with a fake response 
def fake_db_token(monkeypatch, token="TEST_TOKEN"):
    def fake_post(url, data=None, json=None, headers=None, **kwargs):
        return FakeResponse(200, "OK", json_data={"access_token": token})

    def fake_get(url, headers=None, **kwargs):
        raise AssertionError("GET should be overridden per test")

    monkeypatch.setattr(dash_app.requests, "post", fake_post)
    monkeypatch.setattr(dash_app.requests, "get", fake_get)


#verifies that authorisation header is properly sent 
def assert_auth_header(headers):
    assert headers is not None, "No headers passed to requests.get"
    auth = headers.get("Authorization", "")
    assert auth.startswith("Bearer "), f"Error with header: {headers}"


#tests that the home page renders correctly 
def test_home_render(client, monkeypatch):
    fake_db_token(monkeypatch)

    telemetry = [
        {"telemetry_type": "money_spent", "dateTime": "2026-01-01T00:00:00", "data": {"amount": 150}},
        {"telemetry_type": "enemies_destroyed", "dateTime": "2026-01-01T00:01:00", "data": {}},
    ]

    def fake_get(url, headers=None, **kwargs):
        assert url.endswith("/telemetry")
        assert_auth_header(headers)
        return FakeResponse(200, "OK", json_data=telemetry)

    monkeypatch.setattr(dash_app.requests, "get", fake_get)

    r = client.get("/")
    assert r.status_code == 200
    assert "Dashboard" in r.text


#tests that the dashboard page loads correctly and shows telemetry 
def test_dashboard_page_render(client, monkeypatch):
    fake_db_token(monkeypatch)

    telemetry = [
        {"telemetry_type": "money_spent", "dateTime": "2026-01-01T00:00:00", "user_id": 1, "stage_id": 1, "data": {"amount": 10}},
    ]

    def fake_get(url, headers=None, **kwargs):
        assert url.endswith("/telemetry")
        assert_auth_header(headers)
        return FakeResponse(200, "OK", json_data=telemetry)

    monkeypatch.setattr(dash_app.requests, "get", fake_get)

    r = client.get("/dashboard")
    assert r.status_code == 200
    assert "Telemetry" in r.text


#tests what happens when backend returns an error
def test_decisionlog_returns_error(client, monkeypatch):
    fake_db_token(monkeypatch)

    def fake_get(url, headers=None, **kwargs):
        return FakeResponse(ok=False, status_code=503, text="backend down")

    monkeypatch.setattr(dash_app.requests, "get", fake_get)

    r = client.get("/decisionLog")
    assert r.status_code == 503
    assert "backend down" in r.text


#tests what happens when the backend returns a response that isn't json 
def test_parameter_returns_error(client, monkeypatch):
    fake_db_token(monkeypatch)

    def fake_get(url, headers=None, **kwargs):
        return FakeResponse(
            status_code=200,
            text="<html>not json</html>",
            headers={"content-type": "text/html"},
            json_raises=True,
        )

    monkeypatch.setattr(dash_app.requests, "get", fake_get)

    r = client.get("/parameters")
    assert r.status_code == 500
    assert "did not return JSON" in r.text


#tests paraneters page renders correctly 
def test_parameters_page_contains_table_headers(client, monkeypatch):
    fake_db_token(monkeypatch)

    params = [{"name": "enemy_damage_multiplier", "value": 1.5}]

    def fake_get(url, headers=None, **kwargs):
        assert_auth_header(headers)
        if url.endswith("/telemetry"):
            return FakeResponse(200, "OK", json_data=[])
        if "/parameters" in url:
            return FakeResponse(200, "OK", json_data=[
                {"name": "enemy_damage_multiplier", "value": 1.5}
            ])
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(dash_app.requests, "get", fake_get)

    r = client.get("/parameters")
    assert r.status_code == 200
    assert "Parameter Name" in r.text
    assert "Value" in r.text