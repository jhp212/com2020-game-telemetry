import pytest
from fastapi.testclient import TestClient #fastapi test client 

import dashboard.app as dashboard_app

#this pytest fixture creates a test client for the fast api app
#will run before any test that takes client as a parameter 
@pytest.fixture
def client():
    with TestClient(dashboard_app.app) as c: #creates a test client 
        yield c #yield it to the test function

