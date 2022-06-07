from fastapi.testclient import TestClient

from auth_ms import __version__
from auth_ms.main import app
from auth_ms.helpers import get_current_user


client = TestClient(app)


def test_version():
    assert __version__ == "0.1.0"


def test_token():
    # Hitting endpoint with a GET Request
    endpoint = "/token"
    response = client.get(endpoint)
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    # Hitting endpoint with a post request with no user credentials
    response = client.post(endpoint)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "username"],
                "msg": "field required",
                "type": "value_error.missing",
            },
            {
                "loc": ["body", "password"],
                "msg": "field required",
                "type": "value_error.missing",
            },
        ]
    }

    # Providing invalid user credentials

    """
    Reference:
    curl -X 'POST' \
    'http://localhost:3000/token' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'grant_type=&username=invaliduser&password=password&scope=&client_secret='
    ---
    http --form :3000/token \
    accept:application/json
    Content-Type:application/x-www-form-urlencoded \
    grant_type= username=invaliduser password=password scope= client_secret=
    """
    response = client.post(
        endpoint,
        headers={
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data="grant_type=&username=invaliduser&password=password&scope=&client_secret=",
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

    # Providing valid user credentials
    response = client.post(
        endpoint,
        headers={
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data="grant_type=&username=johndoe&password=secret&scope=&client_secret=",
    )
    assert response.status_code == 200
    token = response.json().get("access_token")
    user = get_current_user(token=token)
    assert "johndoe" == user.username


def test_users_me():
    endpoint = "/users/me"

    """
    Reference:
    curl -X 'GET' \
    'http://localhost:3000/users/me' \
    ---
    http :3000/users/me
    """
    response = client.get(endpoint)

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    """
    curl -X 'GET' \
    'http://localhost:3000/users/me' \
    -H 'accept: application/json' \
    -H 'Authorization: Bearer invalid_token'
    ---
    http :3000/users/me \
    accept:application/json Authorization:"Bearer invalid_token"
    """
    response = client.get(
        endpoint,
        headers={
            "accept": "application/json",
            "Authorization": "Bearer invalid_token",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}

    """
    curl -X 'GET' \
    'http://localhost:3000/users/me' \
    -H 'accept: application/json' \
    -H 'Authorization: Bearer johndoe'
    ---
    http :3000/users/me \
    accept:application/json Authorization:"Bearer johndoe"
    """
    valid_token = get_good_token()

    response = client.get(
        endpoint,
        headers={
            "accept": "application/json",
            "Authorization": f"Bearer {valid_token}",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "disabled": False,
        "email": "johndoe@example.com",
        "full_name": "John Doe",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "username": "johndoe",
    }


def get_good_token() -> str:
    response = client.post(
        "/token",
        headers={
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data="grant_type=&username=johndoe&password=secret&scope=&client_secret=",
    )

    return response.json().get("access_token")
