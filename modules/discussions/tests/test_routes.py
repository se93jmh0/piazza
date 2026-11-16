from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError

from tests.conftest import client, session_frobbers


def test_create_discussion_post(client):
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

    before_post = datetime.now(timezone.utc)
    response = client.post(
        "/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "foo",
            "body": "bar",
            "expires_at": "2026-11-14T15:42:38Z",
            "topics": ["Tech"],
        },
    )

    assert response.status_code == 201
    post = response.json()
    assert post["id"] >= 0
    assert post["author"] == "user@example.com"
    assert (
        datetime.strptime(post["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
        >= before_post
    )
    assert post["title"] == "foo"
    assert post["body"] == "bar"
    assert post["expires_at"] == "2026-11-14T15:42:38Z"
    assert post["topics"] == ["Tech"]


def test_create_discussion_post_unknown_topic(client):
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

    before_post = datetime.now(timezone.utc)
    response = client.post(
        "/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "foo",
            "body": "bar",
            "expires_at": "2026-11-14T15:42:38Z",
            "topics": ["baz"],
        },
    )

    assert response.status_code == 422
    assert "baz" in response.json()["detail"]


def test_create_discussion_post_unauthd(client):
    response = client.post("/posts")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_create_discussion_post_encounters_SQLAlchemyError(
    client, session_frobbers
):
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

    def commit_throws_SQLAlchemyError(session):
        def throw_integrity_error():
            raise SQLAlchemyError("Uh-Oh! :(")

        session.commit = throw_integrity_error

    session_frobbers.append(commit_throws_SQLAlchemyError)

    before_post = datetime.now(timezone.utc)
    response = client.post(
        "/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "foo",
            "body": "bar",
            "expires_at": "2026-11-14T15:42:38Z",
            "topics": ["Tech"],
        },
    )

    assert response.status_code == 500
    assert "Uh-Oh! :(" in response.json()["detail"]


def test_add_discussion_post_comment(client):
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
    response = client.post(
        "/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "foo",
            "body": "bar",
            "expires_at": "2026-11-14T15:42:38Z",
            "topics": ["Tech"],
        },
    )
    assert response.status_code == 201
    post_id = response.json()["id"]

    before_comment = datetime.now(timezone.utc)
    response = client.post(
        f"/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "body": "frob",
        },
    )

    assert response.status_code == 201
    comment = response.json()
    assert comment["id"] >= 0
    assert comment["author"] == "user@example.com"
    assert (
        datetime.strptime(comment["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
        >= before_comment
    )
    assert comment["body"] == "frob"


def test_add_discussion_post_comment_unknown_post(client):
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

    before_comment = datetime.now(timezone.utc)
    response = client.post(
        f"/posts/1234567890/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "body": "frob",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Unknown post ID: 1234567890"


def test_add_discussion_post_comment_encounters_SQLAlchemyError(
    client, session_frobbers
):
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
    response = client.post(
        "/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "foo",
            "body": "bar",
            "expires_at": "2026-11-14T15:42:38Z",
            "topics": ["Tech"],
        },
    )
    assert response.status_code == 201
    post_id = response.json()["id"]

    def commit_throws_SQLAlchemyError(session):
        def throw_integrity_error():
            raise SQLAlchemyError("Uh-Oh! :(")

        session.commit = throw_integrity_error

    session_frobbers.append(commit_throws_SQLAlchemyError)

    before_comment = datetime.now(timezone.utc)
    response = client.post(
        f"/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "body": "frob",
        },
    )

    assert response.status_code == 500
    assert "Uh-Oh! :(" in response.json()["detail"]
