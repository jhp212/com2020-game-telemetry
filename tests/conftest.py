import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#adds project root to python path, allows tests to import modules ocrrectly
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#database and db utilities 
from database.main import app as db_app
from database.database import get_db
from database.models import Base, Users
from database.security import get_password_hash, create_access_token

import dashboard.app as dash_app


#creating the test database engine
#uses sqlite test database which is separtae from actual dv 
engine = create_engine(
    "sqlite:///./test.db",
    connect_args={"check_same_thread": False},
)
#creates session factory for testing 
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


#setup and take down test database 
@pytest.fixture(scope="session", autouse=True)
def setup_db():
    #drops and recreate tables before tests start 
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield #run tests 
    #drop all tables ater tests finish 
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

#creating a database session per test 
@pytest.fixture
def db_session():
    #open connection and start transaction 
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session #yield session to tests 
    finally:
        #rollback cahnges after each test 
        session.close()
        transaction.rollback()
        connection.close()


#test client for database api 
@pytest.fixture
def db_client(db_session):
    #overrides fastapi dependency to use test db session
    def override_get_db():
        yield db_session

    db_app.dependency_overrides[get_db] = override_get_db
    #creates test client 
    with TestClient(db_app) as c:
        yield c
    #clears overrides after test 
    db_app.dependency_overrides.clear()


#for authentication 
@pytest.fixture
def test_credentials():
    #admin login credentials 
    return {"username": "testadmin", "password": "adminpass"}

#ensures test user exists 
@pytest.fixture
def ensure_test_user(db_session, test_credentials):
    #checks if user already exists 
    user = db_session.query(Users).filter(Users.username == test_credentials["username"]).first()
    #creates user if not 
    if not user:
        user = Users(
            username=test_credentials["username"],
            password_hash=get_password_hash(test_credentials["password"]),
            is_admin=1,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user

#creates access token for the test user 
@pytest.fixture
def access_token(ensure_test_user, test_credentials):
    return create_access_token({"sub": test_credentials["username"]})

#authorisation header 
@pytest.fixture
def auth_headers(access_token):
    return {"Authorization": f"Bearer {access_token}"}

#authenticated database client 
@pytest.fixture
def auth_db_client(db_client, auth_headers):
    db_client.headers.update(auth_headers)
    return db_client


#dashboard integration client 
# simulates dahsboard calling database api using requests  
@pytest.fixture
def dashboard_client(auth_db_client, monkeypatch):
    #fake response object to mimic requests.Response 
    class FakeResponse:
        def __init__(self, status_code, text, json_data=None, headers=None):
            self.status_code = status_code
            self.text = text
            self._json_data = json_data
            self.ok = 200 <= status_code < 300
            self.headers = headers or {"content-type": "application/json"}

        def json(self):
            if self._json_data is None:
                raise ValueError("There is no JSON")
            return self._json_data

    #converts full url to internal api path 
    def _to_path(url: str) -> str:
        return "/" + url.split("/", 3)[-1]

    #dashboard gets token through requests.post("/auth/token")
    #fake requests.post
    def fake_post(url, data=None, json=None, headers=None, **kwargs):
        #handles the token request
        if url.endswith("/auth/token"):
            token = auth_db_client.headers["Authorization"].replace("Bearer ", "")
            return FakeResponse(200, "OK", {"access_token": token})
        #forward other POST requests to test db client 
        path = _to_path(url)
        r = auth_db_client.post(path, data=data, json=json, headers=headers, params=kwargs.get("params"))
        try:
            return FakeResponse(r.status_code, r.text, r.json(), headers=dict(r.headers))
        except Exception:
            return FakeResponse(r.status_code, r.text, None, headers=dict(r.headers))

    #fake requests.get 
    def fake_get(url, **kwargs):
        path = _to_path(url)
        r = auth_db_client.get(
            path,
            params=kwargs.get("params"),
            headers=kwargs.get("headers"),
        )
        try:
            return FakeResponse(r.status_code, r.text, r.json(), headers=dict(r.headers))
        except Exception:
            return FakeResponse(r.status_code, r.text, None, headers=dict(r.headers))
    
    #replaces requests in dashboard app with fake functions 
    monkeypatch.setattr(dash_app.requests, "post", fake_post)
    monkeypatch.setattr(dash_app.requests, "get", fake_get)

    #return dashboard test client
    with TestClient(dash_app.app) as c:
        yield c


#dhasboard init test client 
#used when requests.get/post is faked inside the individual tests 
@pytest.fixture
def dashboard_unit_client():
    with TestClient(dash_app.app) as c:
        yield c



#keeps the old fixtures (before I refactorijng testing to improve readability) so old tests dont break
@pytest.fixture
def auth_client(auth_db_client):
    return auth_db_client


@pytest.fixture
def client(dashboard_unit_client):
    return dashboard_unit_client