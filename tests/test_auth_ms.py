from fastapi.testclient import TestClient

from auth_ms import __version__
from auth_ms.main import app


client = TestClient(app)


def test_version():
    assert __version__ == '0.1.0'


def test_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
