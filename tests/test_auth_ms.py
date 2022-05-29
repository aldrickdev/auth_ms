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
        "/protected",
        headers={"accept": "application/json", "Authorization": "Bearer johndoe"},
    )
    assert response.status_code == 200
    assert response.json() == {"token": "johndoe"}

    response = client.get(
        "/protected",
        headers={"accept": "application/json", "Authorization": "Bearer bad_token"},
    )
    assert response.status_code == 200
    assert response.json() == {"token": "bad_token"}
