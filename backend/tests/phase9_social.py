"""Phase 9 integration tests: social feed endpoint."""

from __future__ import annotations

from secrets import token_hex
from uuid import uuid4

from fastapi.testclient import TestClient

from src.app.main import app


def _register_and_login(client: TestClient, prefix: str) -> dict[str, str]:
    suffix = token_hex(4)
    username = f"{prefix}_{suffix}"
    email = f"{username}@example.com"
    password = "password123"

    r = client.post("/api/v1/auth/register", json={"username": username, "email": email, "password": password})
    assert r.status_code == 201, r.text
    user_id = r.json()["id"]

    l = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert l.status_code == 200, l.text
    access_token = l.json()["access_token"]
    return {"user_id": user_id, "access_token": access_token}


def _existing_media_id(client: TestClient, headers: dict[str, str]) -> str:
    """Fetch an existing media id so FK constraints pass in integration tests."""
    res = client.get("/api/v1/media/search?query=a&limit=1&offset=0", headers=headers)
    assert res.status_code == 200, res.text
    items = res.json().get("items", [])
    assert items, "Expected at least one media entry in test database"
    return items[0]["id"]


def test_phase9_social_feed_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.get("/api/v1/social/feed")
        assert res.status_code == 401


def test_phase9_social_feed_returns_shared_group_member_activity_only() -> None:
    with TestClient(app) as client:
        viewer = _register_and_login(client, "viewer")
        friend = _register_and_login(client, "friend")
        outsider = _register_and_login(client, "outsider")

        viewer_headers = {"Authorization": f"Bearer {viewer['access_token']}"}
        friend_headers = {"Authorization": f"Bearer {friend['access_token']}"}
        outsider_headers = {"Authorization": f"Bearer {outsider['access_token']}"}

        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Phase9 Group", "description": "social feed test", "is_private": True},
            headers=viewer_headers,
        )
        assert group_create.status_code == 201, group_create.text
        invite_code = group_create.json()["invite_code"]

        join_res = client.post(f"/api/v1/groups/join/{invite_code}", headers=friend_headers)
        assert join_res.status_code == 200, join_res.text

        media_id = _existing_media_id(client, viewer_headers)

        # Friend activity should appear in viewer feed.
        friend_entry = client.post(
            "/api/v1/lists",
            json={"media_id": media_id, "status": "watching", "progress": 3},
            headers=friend_headers,
        )
        assert friend_entry.status_code == 201, friend_entry.text

        # Viewer own activity should be excluded from feed.
        viewer_entry = client.post(
            "/api/v1/lists",
            json={"media_id": media_id, "status": "watching", "progress": 1},
            headers=viewer_headers,
        )
        assert viewer_entry.status_code == 201, viewer_entry.text

        # Outsider activity should be excluded from feed.
        outsider_entry = client.post(
            "/api/v1/lists",
            json={"media_id": media_id, "status": "watching", "progress": 10},
            headers=outsider_headers,
        )
        assert outsider_entry.status_code == 201, outsider_entry.text

        feed_res = client.get("/api/v1/social/feed", headers=viewer_headers)
        assert feed_res.status_code == 200, feed_res.text

        body = feed_res.json()
        assert "items" in body
        assert isinstance(body["items"], list)
        assert body["total"] >= 1

        actor_ids = {item["user_id"] for item in body["items"]}
        assert friend["user_id"] in actor_ids
        assert viewer["user_id"] not in actor_ids
        assert outsider["user_id"] not in actor_ids


def test_phase9_recommend_requires_shared_group_and_prevents_self() -> None:
    with TestClient(app) as client:
        sender = _register_and_login(client, "sender")
        receiver = _register_and_login(client, "receiver")

        sender_headers = {"Authorization": f"Bearer {sender['access_token']}"}

        # self-recommendation is invalid
        self_res = client.post(
            "/api/v1/social/recommend",
            json={"to_user_id": sender["user_id"], "media_id": str(uuid4()), "message": "watch this"},
            headers=sender_headers,
        )
        assert self_res.status_code == 400, self_res.text

        # recommendation without shared group is invalid
        no_group_res = client.post(
            "/api/v1/social/recommend",
            json={"to_user_id": receiver["user_id"], "media_id": str(uuid4()), "message": "watch this"},
            headers=sender_headers,
        )
        assert no_group_res.status_code == 400, no_group_res.text


def test_phase9_recommend_creates_recommendation_for_shared_group_member() -> None:
    with TestClient(app) as client:
        sender = _register_and_login(client, "senderok")
        receiver = _register_and_login(client, "receiverok")

        sender_headers = {"Authorization": f"Bearer {sender['access_token']}"}
        receiver_headers = {"Authorization": f"Bearer {receiver['access_token']}"}

        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Recommend Group", "description": "phase 9.2", "is_private": True},
            headers=sender_headers,
        )
        assert group_create.status_code == 201, group_create.text
        invite_code = group_create.json()["invite_code"]

        join_res = client.post(f"/api/v1/groups/join/{invite_code}", headers=receiver_headers)
        assert join_res.status_code == 200, join_res.text

        media_id = _existing_media_id(client, sender_headers)

        rec_res = client.post(
            "/api/v1/social/recommend",
            json={"to_user_id": receiver["user_id"], "media_id": media_id, "message": "you will like this"},
            headers=sender_headers,
        )
        assert rec_res.status_code == 201, rec_res.text
        body = rec_res.json()
        assert body["from_user_id"] == sender["user_id"]
        assert body["to_user_id"] == receiver["user_id"]
        assert body["is_acknowledged"] is False


def test_phase9_recommendation_inbox_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.get("/api/v1/social/recommendations/inbox")
        assert res.status_code == 401


def test_phase9_recommendation_inbox_returns_only_current_user_items() -> None:
    with TestClient(app) as client:
        sender = _register_and_login(client, "senderinbox")
        receiver = _register_and_login(client, "receiverinbox")
        third = _register_and_login(client, "thirdinbox")

        sender_headers = {"Authorization": f"Bearer {sender['access_token']}"}
        receiver_headers = {"Authorization": f"Bearer {receiver['access_token']}"}

        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Inbox Group", "description": "phase 9.3", "is_private": True},
            headers=sender_headers,
        )
        assert group_create.status_code == 201, group_create.text
        invite_code = group_create.json()["invite_code"]

        join_receiver = client.post(f"/api/v1/groups/join/{invite_code}", headers=receiver_headers)
        assert join_receiver.status_code == 200, join_receiver.text

        media_id = _existing_media_id(client, sender_headers)

        # sender -> receiver (should appear in receiver inbox)
        rec_ok = client.post(
            "/api/v1/social/recommend",
            json={"to_user_id": receiver["user_id"], "media_id": media_id, "message": "for receiver"},
            headers=sender_headers,
        )
        assert rec_ok.status_code == 201, rec_ok.text

        # sender -> third user in another shared group (must NOT appear in receiver inbox)
        group_create_2 = client.post(
            "/api/v1/groups",
            json={"name": "Other Group", "description": "phase 9.3 other", "is_private": True},
            headers=sender_headers,
        )
        assert group_create_2.status_code == 201, group_create_2.text
        invite_code_2 = group_create_2.json()["invite_code"]
        third_headers = {"Authorization": f"Bearer {third['access_token']}"}
        join_third = client.post(f"/api/v1/groups/join/{invite_code_2}", headers=third_headers)
        assert join_third.status_code == 200, join_third.text

        rec_other = client.post(
            "/api/v1/social/recommend",
            json={"to_user_id": third["user_id"], "media_id": media_id, "message": "for third"},
            headers=sender_headers,
        )
        assert rec_other.status_code == 201, rec_other.text

        inbox_res = client.get("/api/v1/social/recommendations/inbox", headers=receiver_headers)
        assert inbox_res.status_code == 200, inbox_res.text
        body = inbox_res.json()

        assert isinstance(body["items"], list)
        assert body["total"] >= 1
        assert body["limit"] == 50
        assert body["offset"] == 0

        recipients = {item["to_user_id"] for item in body["items"]}
        assert recipients == {receiver["user_id"]}
