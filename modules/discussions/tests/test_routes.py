from datetime import datetime, timezone
from unittest.mock import Mock

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

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


def test_react_to_discussion_post_like(client):
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

    response = client.put(
        f"/posts/{post_id}/reaction",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": "like"},
    )

    assert response.status_code == 200
    reaction_counts = response.json()
    assert reaction_counts["post_id"] == post_id
    assert reaction_counts["likes"] == 1
    assert reaction_counts["dislikes"] == 0


def test_react_to_discussion_post_dislike(client):
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

    response = client.put(
        f"/posts/{post_id}/reaction",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": "dislike"},
    )

    assert response.status_code == 200
    reaction_counts = response.json()
    assert reaction_counts["post_id"] == post_id
    assert reaction_counts["likes"] == 0
    assert reaction_counts["dislikes"] == 1


def test_react_to_discussion_post_unknown_post(client):
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
    response = client.put(
        f"/posts/1234567890/reaction",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": "like"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Unknown post ID: 1234567890"


def test_react_to_discussion_post_invalid_value(client):
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

    response = client.put(
        f"/posts/{post_id}/reaction",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": "pooh-pooh"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid reaction: 'pooh-pooh'"


def test_react_to_discussion_post_encounters_SQLAlchemyError(
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

    response = client.put(
        f"/posts/{post_id}/reaction",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": "like"},
    )

    assert response.status_code == 500
    assert "Uh-Oh! :(" in response.json()["detail"]


def test_get_discussion_post(client):
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
    post_id = response.json()["id"]

    response = client.get(
        f"/posts/{post_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
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
    assert post["comments"] == []
    assert post["likes"] == 0
    assert post["dislikes"] == 0


def test_get_discussion_post_unknown_post(client):
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
        f"/posts/1234567890", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Unknown post ID: 1234567890"


def test_get_discussion_post_encounters_SQLAlchemyError(
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
    response = client.get(
        f"/posts/1234567890", headers={"Authorization": f"Bearer {token}"}
    )

    def get_throws_SQLAlchemyError(session):
        def throw_SQLAlchemyError(*args, **kwargs):
            raise SQLAlchemyError("Uh-Oh! :(")

        session.get = throw_SQLAlchemyError

    session_frobbers.append(get_throws_SQLAlchemyError)

    response = client.get(
        f"/posts/1234567890", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 500
    assert "Uh-Oh! :(" in response.json()["detail"]


def test_get_discussion_posts(client):
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
    post_id = response.json()["id"]

    response = client.get(
        f"/posts", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    posts = response.json()
    assert len(posts) == 1
    post = posts[0]
    assert post["id"] == post_id
    assert post["author"] == "user@example.com"
    assert (
        datetime.strptime(post["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
        >= before_post
    )
    assert post["title"] == "foo"
    assert post["body"] == "bar"
    assert post["expires_at"] == "2026-11-14T15:42:38Z"
    assert post["topics"] == ["Tech"]
    assert post["comments"] == []
    assert post["likes"] == 0
    assert post["dislikes"] == 0


def test_get_discussion_posts_encounters_SQLAlchemyError(
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

    def query_throws_SQLAlchemyError(session: Session):
        def throw_SQLAlchemyError(*args, **kwargs):
            raise SQLAlchemyError("Uh-Oh! :(")

        session.scalars = Mock(
            wraps=session.scalars,
            side_effect=throw_SQLAlchemyError,
        )

    session_frobbers.append(query_throws_SQLAlchemyError)

    response = client.get(
        f"/posts", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 500
    assert "Uh-Oh! :(" in response.json()["detail"]


def test_get_discussion_posts_with_topic_filter(client):
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
            "title": "Politics Post 0",
            "body": "Lorem ipsum",
            "expires_at": "2026-11-14T15:42:38Z",
            "topics": ["Politics"],
        },
    )
    assert response.status_code == 201
    response = client.post(
        "/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Tech Post 0",
            "body": "Lorem ipsum",
            "expires_at": "2026-11-14T15:42:38Z",
            "topics": ["Tech"],
        },
    )
    assert response.status_code == 201
    tech_post_id = response.json()["id"]
    response = client.post(
        "/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Politics Post 1",
            "body": "Lorem ipsum",
            "expires_at": "2026-11-14T15:42:38Z",
            "topics": ["Politics"],
        },
    )
    assert response.status_code == 201

    response = client.get(
        f"/posts?topic=Tech", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    posts = response.json()
    assert len(posts) == 1
    assert posts[0]["id"] == tech_post_id
