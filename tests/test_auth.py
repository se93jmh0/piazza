from unittest.mock import MagicMock

from sqlalchemy.exc import IntegrityError

from security import hash_password, verify_password


def test_register_happy_path(client):
    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "hunter2"},
    )

    assert response.status_code == 201
    user = response.json()
    assert user["email"] == "user@example.com"
    assert user["id"] >= 0


def test_register_existing_user(client):
    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "hunter2"},
    )
    assert response.status_code == 201

    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "hunter3"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"


def test_register_password_too_short(client):
    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "4"},
    )

    assert response.status_code == 422
    assert any(
        detail["loc"] == ["body", "password"]
        for detail in response.json()["detail"]
    )


def test_register_encounters_db_integrity_error(client, session_frobbers):
    def commit_throws_integrity_error(session):
        def throw_integrity_error():
            raise IntegrityError(MagicMock(), MagicMock(), MagicMock())

        session.commit = throw_integrity_error

    session_frobbers.append(commit_throws_integrity_error)

    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "hunter2"},
    )

    assert response.status_code == 409


def test_login_happy_path(client):
    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "hunter2"},
    )
    assert response.status_code == 201

    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "hunter2"},
    )

    assert response.status_code == 200


def test_login_unknown_user(client):
    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "hunter2"},
    )

    assert response.status_code == 401


def test_login_incorrect_password(client):
    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "hunter2"},
    )
    assert response.status_code == 201

    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "hunter3"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_hiya_happy_path(client):
    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "hunter2"},
    )
    assert response.status_code == 201
    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "hunter2"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.get(
        "/auth/hiya", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert "user@example.com" in response.json()["greeting"]


def test_hiya_unauthd(client):
    response = client.get("/auth/hiya")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
