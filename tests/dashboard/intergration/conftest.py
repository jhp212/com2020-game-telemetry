import pytest
from fastapi.testclient import TestClient

import dashboard.app as dash_app
from database.main import app as db_app, get_db


#provides a test client for the database API
#overrides the database dependency so the API uses the test db
@pytest.fixture
def db_client(db_session):
    #replaces get_db with the test session
    def override_get_db():
        yield db_session

    #replace the real get_db dependency with the test version
    db_app.dependency_overrides[get_db] = override_get_db

    #creates a test client which is used to simulate requests to the db API
    with TestClient(db_app) as c:
        yield c

    #removes the dependency override after tests completes
    db_app.dependency_overrides.clear()


#provides a test client for the dashboard 
#intercepts http requests and redirects them to the test database API
#necessary because the dashboard normally makes real http requests to the database API
@pytest.fixture
def dashboard_client(db_client, monkeypatch):

    #mimics the behaviour of requests.Response which is used by the dashboard
    #neccessary because the dashboard expects responses in the same format as requests.get
    class FakeResponse:
        def __init__(self, status_code, text, json_data=None):
            self.status_code = status_code
            self.text = text
            self._json_data = json_data
            self.ok = 200 <= status_code < 300
            self.headers = {"content-type": "application/json"}

        def json(self):
            if self._json_data is None:
                raise ValueError("There is no JSON")
            return self._json_data

    #replaces requests.get in dashboard.app
    #this forwards requests to the test client db instead of making real http calls
    def fake_get(url, **kwargs):
        #extracts the API path from the url
        path = "/" + url.split("/", 3)[-1]

        #forwards the request to the test client db
        r = db_client.get(path, params=kwargs.get("params"))
        try:
            return FakeResponse(r.status_code, r.text, r.json())
        except Exception:
            return FakeResponse(r.status_code, r.text, None)

    #monkeypatch replaces requests.get only inside dashboard.app
    #ensures that this change is only applied to the test and doesn't affect the real code
    monkeypatch.setattr(dash_app.requests, "get", fake_get)

    #create a test client for the dashboard routes
    with TestClient(dash_app.app) as c:
        yield c
