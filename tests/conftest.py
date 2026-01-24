import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


#assumes the database directory is one level above the parent directory of conftest.py 
#may need to be changed as project layout evolves 
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database.main import Base, app, get_db  

#creating an database engine just for tests so real data isn't affected
engine = create_engine("sqlite:///./test.db")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#runs before and then after all tests
#db setup and removal 
@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine) #removes all existing tables 
    Base.metadata.create_all(bind=engine) #creats all tables in the model
    yield #this yeilds control to the test suite 
    Base.metadata.drop_all(bind=engine) #drops all tables after all tests have run 
    engine.dispose() #gets rid of the engine 

#this makes sure each tests runs inside its own transaction and any changes are rolled back after tests
@pytest.fixture
def db_session():
    connection = engine.connect() 
    transaction = connection.begin()


    session = TestingSessionLocal(bind=connection)
    try:
        yield session #yields session to the test suit
    finally: #closes session, roll back changes, and closes the connection
        session.close() 
        transaction.rollback()
        connection.close()

#this overrides get_db
#neccessary so that the API routes use the test db and not the real one 
@pytest.fixture
def client(db_session):
    #replaces get_db with the test session 
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    #creates a test client which simulate http requests to the API 
    with TestClient(app) as c:
        yield c
    #remove the dependency override after the test    
    app.dependency_overrides.clear()
