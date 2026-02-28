import jwt
import pytest
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

from database.security import ALGORITHM, SECRET_KEY, create_access_token, get_current_user


#example json for post to /parameters/ 
PARAM_PAYLOAD = {"name": "enemy_damage_multiplier", "value": 1.5}


#tests if you can successfully get a valid token from the db 
def test_auth_token_success(db_client, ensure_test_user, test_credentials):
    r = db_client.post(
        "/auth/token",
        data={
            "username": test_credentials["username"],
            "password": test_credentials["password"],
        },
    )

    assert r.status_code == 200, r.text
    data = r.json()

    #token must exist in response 
    assert "access_token" in data, data
    token = data["access_token"]

    #decode jwt and confirm important fields 
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == test_credentials["username"]
    assert "exp" in payload

#tests if authentication is rejected when passing an incorrect password 
def test_auth_token_bad_password(db_client, ensure_test_user, test_credentials):
    r = db_client.post(
        "/auth/token",
        data={
            "username": test_credentials["username"],
            "password": "WRONG_PASSWORD",
        },
    )

    assert r.status_code in (400, 401), r.text

#tests if authentication is rejected when passing an incorrect username  
def test_auth_token_unknown_user(db_client):
    """
    Tests:
    - POST /auth/token rejects unknown users
    """
    r = db_client.post(
        "/auth/token",
        data={
            "username": "no_such_user",
            "password": "whatever",
        },
    )

    assert r.status_code in (400, 401), r.text



#tests if protected endpoints returns an error if token isn't passed 
def test_post_parameters_rejects_missing_token(db_client):
    r = db_client.post("/parameters/", json=PARAM_PAYLOAD)
    assert r.status_code == 401, r.text

#tests if post request fails if an invalid token is passed 
def test_post_parameters_rejects_invalid_token(db_client):
    r = db_client.post(
        "/parameters/",
        json=PARAM_PAYLOAD,
        headers={"Authorization": "Bearer not a real token"},
    )
    assert r.status_code == 401, r.text

#tests if a POST request to a protected endpoint is a success 
def test_post_parameters_accepts_valid_token(db_client, auth_headers):
    r = db_client.post("/parameters/", json=PARAM_PAYLOAD, headers=auth_headers)
    assert r.status_code != 401, r.text

#tests if token returned from login works on a protected endpoint 
def test_post_parameters_accepts_login_token(db_client, ensure_test_user, test_credentials):
    login = db_client.post(
        "/auth/token",
        data={
            "username": test_credentials["username"],
            "password": test_credentials["password"],
        },
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    r = db_client.post(
        "/parameters/",
        json=PARAM_PAYLOAD,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code != 401, r.text



#UNIT TESTS 
#tests if tokens are created correctly 
def test_create_access_token_contains_sub_and_exp(test_credentials):
    token = create_access_token({"sub": test_credentials["username"]})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert payload["sub"] == test_credentials["username"]
    assert "exp" in payload

#tests if expired tokens are rejected 
def test_get_current_user_rejects_expired_token(db_session, ensure_test_user, test_credentials):

    expired_payload = {
        "sub": test_credentials["username"],
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1), #sets it to appear expired 
    }
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as e:
        get_current_user(token=expired_token, db=db_session) 

    assert e.value.status_code == 401