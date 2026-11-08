from fastapi.testclient import TestClient

from application import create_app


def test_home():
    client = TestClient(create_app(None))

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["greeting"] == "Welcome to Piazza!"


def test_home2():
    client = TestClient(create_app(None))

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["greeting"] == "Welcome to Piazza!"
