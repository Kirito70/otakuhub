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
from tests.helpers import register_or_login_as_admin


def _register_and_login(client: TestClient, prefix: str) -> dict[str, str]:
    suffix = token_hex(4)
    username = f"{prefix}_{suffix}"
    email = f"{username}@example.com"
    password = "password123"

    return register_or_login_as_admin(client, username, email, password)


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


def test_phase11_notification_preferences_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.get("/api/v1/notifications/preferences")
        assert res.status_code == 401


def test_phase11_notification_preferences_get_returns_defaults_for_new_user() -> None:
    with TestClient(app) as client:
        user = _register_and_login(client, "notifprefs")
        headers = {"Authorization": f"Bearer {user['access_token']}"}

        res = client.get("/api/v1/notifications/preferences", headers=headers)
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["user_id"] == user["user_id"]
        assert body["new_episode"] is True
        assert body["new_chapter"] is True
        assert body["friend_activity"] is True
        assert body["recommendations"] is True
        assert body["watch_party_invite"] is True
        assert body["watch_party_reminder"] is True
        assert body["email_enabled"] is False
        assert body["push_enabled"] is False


def test_phase11_notification_preferences_patch_updates_fields() -> None:
    with TestClient(app) as client:
        user = _register_and_login(client, "notifprefsupd")
        headers = {"Authorization": f"Bearer {user['access_token']}"}

        patch_res = client.patch(
            "/api/v1/notifications/preferences",
            headers=headers,
            json={
                "new_episode": False,
                "watch_party_reminder": False,
                "email_enabled": True,
                "telegram_chat_id": "123456",
            },
        )
        assert patch_res.status_code == 200, patch_res.text

        body = patch_res.json()
        assert body["new_episode"] is False
        assert body["watch_party_reminder"] is False
        assert body["email_enabled"] is True
        assert body["telegram_chat_id"] == "123456"

        get_res = client.get("/api/v1/notifications/preferences", headers=headers)
        assert get_res.status_code == 200, get_res.text
        persisted = get_res.json()
        assert persisted["new_episode"] is False
        assert persisted["watch_party_reminder"] is False
        assert persisted["email_enabled"] is True
        assert persisted["telegram_chat_id"] == "123456"


def test_phase11_mark_all_read_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.post("/api/v1/notifications/mark-all-read")
        assert res.status_code == 401


def test_phase11_mark_all_read_returns_zero_when_no_unread() -> None:
    with TestClient(app) as client:
        user = _register_and_login(client, "markreadempty")
        headers = {"Authorization": f"Bearer {user['access_token']}"}

        res = client.post("/api/v1/notifications/mark-all-read", headers=headers)
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["updated_count"] == 0


def test_phase11_mark_all_read_returns_success() -> None:
    with TestClient(app) as client:
        user = _register_and_login(client, "markread")
        headers = {"Authorization": f"Bearer {user['access_token']}"}

        res = client.post("/api/v1/notifications/mark-all-read", headers=headers)
        assert res.status_code == 200, res.text
        body = res.json()
        assert isinstance(body["updated_count"], int)
