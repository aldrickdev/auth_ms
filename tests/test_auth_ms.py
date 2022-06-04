from fastapi.testclient import TestClient

from auth_ms import __version__
from auth_ms.main import app


client = TestClient(app)


def test_version():
    assert __version__ == "0.1.0"


def test_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_protected():
    endpoint = "/protected"
    response = client.get("/protected")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    """
    curl -X 'GET' \
    'http://localhost:3000/protected' \
    -H 'accept: application/json' \
    -H 'Authorization: Bearer johndoe'
    """
    response = client.get(
        endpoint,
        headers={"accept": "application/json", "Authorization": "Bearer johndoe"},
    )
    assert response.status_code == 200
    assert response.json() == {"token": "johndoe"}

    response = client.get(
        endpoint,
        headers={"accept": "application/json", "Authorization": "Bearer bad_token"},
    )
    assert response.status_code == 200
    assert response.json() == {"token": "bad_token"}

    # Test protected with a good token
    good_token = get_good_token()
    response = client.get(
        endpoint,
        headers={"accept": "application/json", "Authorization": f"Bearer {good_token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"token": "johndoe"}


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
    assert response.status_code == 400
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
    assert response.json() == {"access_token": "johndoe", "token_type": "bearer"}


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
    assert response.json() == {"detail": "Invalid Authentication Credentials"}

    """
    curl -X 'GET' \
    'http://localhost:3000/users/me' \
    -H 'accept: application/json' \
    -H 'Authorization: Bearer johndoe'
    ---
    http :3000/users/me \
    accept:application/json Authorization:"Bearer johndoe"
    """
    response = client.get(
        endpoint,
        headers={
            "accept": "application/json",
            "Authorization": "Bearer johndoe",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "disabled": False,
        "email": "johndoe@example.com",
        "full_name": "John Doe",
        "hashed_password": "fakehashedsecret",
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
