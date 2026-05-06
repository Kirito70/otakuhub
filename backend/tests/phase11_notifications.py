"""Phase 11 notification worker tests."""

from __future__ import annotations

from secrets import token_hex

from fastapi.testclient import TestClient

from src.app.main import app
from src.app.workers.notification_tasks import (
    send_new_chapter_notifications_task,
    send_new_episode_notifications_task,
    send_watch_party_reminder_notifications_task,
)


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


def test_phase11_new_episode_task_without_events_completes() -> None:
    result = send_new_episode_notifications_task.run(episodes=[])

    assert result["task"] == "notifications.new_episode"
    assert result["status"] == "completed"
    assert result["processed_items"] == 0
    assert result["delivered_items"] == 0


def test_phase11_new_chapter_task_without_events_completes() -> None:
    result = send_new_chapter_notifications_task.run(chapters=[])

    assert result["task"] == "notifications.new_chapter"
    assert result["status"] == "completed"
    assert result["processed_items"] == 0
    assert result["delivered_items"] == 0


def test_phase11_watch_party_reminder_task_without_events_completes() -> None:
    result = send_watch_party_reminder_notifications_task.run(parties=[])

    assert result["task"] == "notifications.watch_party_reminder"
    assert result["status"] == "completed"
    assert result["processed_items"] == 0
    assert result["delivered_items"] == 0


def test_phase11_notifications_list_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.get("/api/v1/notifications")
        assert res.status_code == 401


def test_phase11_notifications_list_returns_empty_payload_for_new_user() -> None:
    with TestClient(app) as client:
        user = _register_and_login(client, "notif")
        headers = {"Authorization": f"Bearer {user['access_token']}"}

        res = client.get("/api/v1/notifications", headers=headers)
        assert res.status_code == 200, res.text

        body = res.json()
        assert body["items"] == []
        assert body["total"] == 0
        assert body["limit"] == 50
        assert body["offset"] == 0


def test_phase11_notifications_mark_read_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.patch("/api/v1/notifications/read", json={"notification_ids": []})
        assert res.status_code == 401


def test_phase11_notifications_mark_read_empty_selection_returns_zero() -> None:
    with TestClient(app) as client:
        user = _register_and_login(client, "notifread")
        headers = {"Authorization": f"Bearer {user['access_token']}"}

        res = client.patch(
            "/api/v1/notifications/read",
            headers=headers,
            json={"notification_ids": []},
        )
        assert res.status_code == 200, res.text
        assert res.json()["updated_count"] == 0
