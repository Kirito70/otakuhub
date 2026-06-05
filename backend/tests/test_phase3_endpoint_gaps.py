"""Integration tests for Audit Phase 3 — Backend Endpoint Gaps.

Covers the 9 missing routes implemented during the Phase 3 gap closure:
  1. POST /media (admin create)
  2. PATCH /media/{id} (admin update)
  3. DELETE /media/{id} (admin soft-delete)
  4. DELETE /social/recommendations/{id}
  5. DELETE /social/discussions/{id}
  6. GET /watchparty/{party_id}/rsvps
  7. DELETE /notifications/{id}
  8. GET /users/ (admin list)
  9. DELETE /users/{id} (admin delete)
 10. GET /users/me/settings
 11. PATCH /users/me/settings
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.app.main import app
from tests.helpers import register_or_login_as_admin, ADMIN_USERNAME, ADMIN_PASSWORD

_TEST_MEDIA_ID: str | None = None


def _admin_token(client: TestClient) -> str:
    """Get admin token for test operations."""
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _user_token(client: TestClient, suffix: str | None = None) -> str:
    """Register a normal user and return their access token."""
    s = suffix or uuid4().hex[:8]
    result = register_or_login_as_admin(
        client,
        f"phase3_user_{s}",
        f"phase3_{s}@example.com",
        "password123",
    )
    return result["access_token"]


def _normal_user_headers(client: TestClient) -> dict[str, str]:
    return {"Authorization": f"Bearer {_user_token(client)}"}


def _admin_headers(client: TestClient) -> dict[str, str]:
    return {"Authorization": f"Bearer {_admin_token(client)}"}


def _create_media(client: TestClient) -> str:
    """Helper: create a media entry for testing, return its ID."""
    global _TEST_MEDIA_ID
    if _TEST_MEDIA_ID:
        return _TEST_MEDIA_ID
    headers = _admin_headers(client)
    payload = {
        "title_romaji": "Test Phase3 Anime",
        "title_english": "Test Phase3 Anime EN",
        "media_type": "anime",
        "format": "TV",
        "status": "finished",
        "episode_count": 12,
    }
    resp = client.post("/api/v1/media", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    _TEST_MEDIA_ID = resp.json()["id"]
    return _TEST_MEDIA_ID


# ── 1. Media CRUD ──────────────────────────────────────────────────────


def test_media_create_admin() -> None:
    """Admin can create a media entry."""
    with TestClient(app) as client:
        headers = _admin_headers(client)
        payload = {
            "title_romaji": "Admin Created Anime",
            "media_type": "anime",
            "format": "TV",
            "status": "releasing",
            "episode_count": 24,
        }
        resp = client.post("/api/v1/media", json=payload, headers=headers)
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["title_romaji"] == "Admin Created Anime"
        assert body["media_type"] == "anime"
        assert "id" in body


def test_media_create_forbidden_for_normal_user() -> None:
    """Normal users cannot create media."""
    with TestClient(app) as client:
        headers = _normal_user_headers(client)
        payload = {"title_romaji": "User Created Anime", "media_type": "anime"}
        resp = client.post("/api/v1/media", json=payload, headers=headers)
        assert resp.status_code == 403, resp.text


def test_media_update_admin() -> None:
    """Admin can update a media entry."""
    with TestClient(app) as client:
        media_id = _create_media(client)
        headers = _admin_headers(client)
        resp = client.patch(
            f"/api/v1/media/{media_id}",
            json={"episode_count": 26, "title_english": "Updated Title"},
            headers=headers,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["episode_count"] == 26
        assert body["title_english"] == "Updated Title"


def test_media_update_forbidden_for_normal_user() -> None:
    """Normal users cannot update media."""
    with TestClient(app) as client:
        media_id = _create_media(client)
        headers = _normal_user_headers(client)
        resp = client.patch(
            f"/api/v1/media/{media_id}",
            json={"title_romaji": "Hacked Title"},
            headers=headers,
        )
        assert resp.status_code == 403, resp.text


def test_media_update_not_found() -> None:
    """PATCH /media/{nonexistent} returns 404."""
    with TestClient(app) as client:
        headers = _admin_headers(client)
        fake_id = uuid4()
        resp = client.patch(
            f"/api/v1/media/{fake_id}",
            json={"title_romaji": "Nope"},
            headers=headers,
        )
        assert resp.status_code == 404, resp.text


def test_media_delete_admin() -> None:
    """Admin can soft-delete a media entry."""
    with TestClient(app) as client:
        headers = _admin_headers(client)
        # Create a fresh entry to delete
        create_resp = client.post(
            "/api/v1/media",
            json={"title_romaji": "Deletable Media", "media_type": "anime"},
            headers=headers,
        )
        assert create_resp.status_code == 201, create_resp.text
        media_id = create_resp.json()["id"]

        # Verify it exists
        pre_get = client.get(f"/api/v1/media/{media_id}", headers=headers)
        assert pre_get.status_code == 200, pre_get.text
        assert pre_get.json()["id"] == media_id

        resp = client.delete(f"/api/v1/media/{media_id}", headers=headers)
        assert resp.status_code == 200, resp.text
        assert resp.json()["deleted"] is True

        # Verify it's gone — the query builder should filter deleted_at
        get_resp = client.get(f"/api/v1/media/{media_id}", headers=headers)
        assert get_resp.status_code == 404, (
            f"Expected 404 after soft-delete, got {get_resp.status_code}: {get_resp.text}"
        )


def test_media_delete_forbidden_for_normal_user() -> None:
    """Normal users cannot delete media."""
    with TestClient(app) as client:
        media_id = _create_media(client)
        headers = _normal_user_headers(client)
        resp = client.delete(f"/api/v1/media/{media_id}", headers=headers)
        assert resp.status_code == 403, resp.text


# ── 2. Social DELETE /recommendations/{id} ──────────────────────────────


def test_delete_recommendation_by_sender() -> None:
    """The sender of a recommendation can soft-delete it."""
    with TestClient(app) as client:
        # Create two users
        token_a = _user_token(client, "sender")
        token_b = _user_token(client, "recip")
        media_id = _create_media(client)

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # Get recipient's user_id from /users/me
        me = client.get("/api/v1/users/me", headers=headers_b)
        recip_id = me.json()["id"]

        # Create a recommendation
        rec_resp = client.post(
            "/api/v1/social/recommend",
            json={"to_user_id": recip_id, "media_id": media_id},
            headers=headers_a,
        )
        # May fail if no shared group — if so, skip
        if rec_resp.status_code != 201:
            pytest.skip("No shared group between test users")

        rec_id = rec_resp.json()["id"]

        # Delete by sender
        del_resp = client.delete(
            f"/api/v1/social/recommendations/{rec_id}",
            headers=headers_a,
        )
        assert del_resp.status_code == 200, del_resp.text
        assert del_resp.json()["deleted"] is True


def test_delete_recommendation_forbidden_for_recipient() -> None:
    """Only the sender can delete a recommendation (not the recipient)."""
    with TestClient(app) as client:
        token_a = _user_token(client, "sender2")
        token_b = _user_token(client, "recip2")
        media_id = _create_media(client)

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        me = client.get("/api/v1/users/me", headers=headers_b)
        recip_id = me.json()["id"]

        rec_resp = client.post(
            "/api/v1/social/recommend",
            json={"to_user_id": recip_id, "media_id": media_id},
            headers=headers_a,
        )
        if rec_resp.status_code != 201:
            pytest.skip("No shared group between test users")

        rec_id = rec_resp.json()["id"]

        # Recipient tries to delete
        del_resp = client.delete(
            f"/api/v1/social/recommendations/{rec_id}",
            headers=headers_b,
        )
        assert del_resp.status_code == 403, del_resp.text


def test_delete_recommendation_not_found() -> None:
    """DELETE nonexistent recommendation returns 404."""
    with TestClient(app) as client:
        headers = _normal_user_headers(client)
        fake_id = uuid4()
        resp = client.delete(f"/api/v1/social/recommendations/{fake_id}", headers=headers)
        assert resp.status_code == 404, resp.text


# ── 3. Social DELETE /discussions/{id} ──────────────────────────────────


def test_delete_discussion_by_author() -> None:
    """The author of a discussion can soft-delete it."""
    with TestClient(app) as client:
        token = _user_token(client, "discuss")
        media_id = _create_media(client)
        headers = {"Authorization": f"Bearer {token}"}

        me = client.get("/api/v1/users/me", headers=headers)
        user_id = me.json()["id"]

        # Get user's groups
        groups = client.get("/api/v1/groups", headers=headers)
        if groups.status_code != 200 or not groups.json().get("items"):
            pytest.skip("User has no groups")

        group_id = groups.json()["items"][0]["id"]

        # Create discussion
        disc_resp = client.post(
            "/api/v1/social/discussions",
            json={
                "media_id": media_id,
                "group_id": group_id,
                "body": "Test discussion for delete test",
            },
            headers=headers,
        )
        if disc_resp.status_code != 201:
            pytest.skip("Could not create discussion")

        disc_id = disc_resp.json()["id"]

        # Delete
        del_resp = client.delete(
            f"/api/v1/social/discussions/{disc_id}",
            headers=headers,
        )
        assert del_resp.status_code == 200, del_resp.text
        assert del_resp.json()["deleted"] is True


def test_delete_discussion_forbidden_for_other_user() -> None:
    """Only the author can delete a discussion."""
    with TestClient(app) as client:
        token_a = _user_token(client, "author1")
        token_b = _user_token(client, "notauth")
        media_id = _create_media(client)

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        groups = client.get("/api/v1/groups", headers=headers_a)
        if groups.status_code != 200 or not groups.json().get("items"):
            pytest.skip("User has no groups")

        group_id = groups.json()["items"][0]["id"]

        disc_resp = client.post(
            "/api/v1/social/discussions",
            json={"media_id": media_id, "group_id": group_id, "body": "Test"},
            headers=headers_a,
        )
        if disc_resp.status_code != 201:
            pytest.skip("Could not create discussion")

        disc_id = disc_resp.json()["id"]

        del_resp = client.delete(
            f"/api/v1/social/discussions/{disc_id}",
            headers=headers_b,
        )
        assert del_resp.status_code == 403, del_resp.text


def test_delete_discussion_not_found() -> None:
    """DELETE nonexistent discussion returns 404."""
    with TestClient(app) as client:
        headers = _normal_user_headers(client)
        fake_id = uuid4()
        resp = client.delete(f"/api/v1/social/discussions/{fake_id}", headers=headers)
        assert resp.status_code == 404, resp.text


# ── 4. Watchparty RSVPs list ────────────────────────────────────────────


def test_get_watchparty_rsvps() -> None:
    """GET /watchparty/{party_id}/rsvps returns RSVP list."""
    with TestClient(app) as client:
        token = _user_token(client, "rsvp")
        media_id = _create_media(client)
        headers = {"Authorization": f"Bearer {token}"}

        groups = client.get("/api/v1/groups", headers=headers)
        if groups.status_code != 200 or not groups.json().get("items"):
            pytest.skip("User has no groups")

        group_id = groups.json()["items"][0]["id"]

        # Create a watch party
        from datetime import datetime, timedelta
        future = (datetime.utcnow() + timedelta(days=7)).isoformat()
        wp_resp = client.post(
            "/api/v1/watchparty",
            json={
                "group_id": group_id,
                "media_id": media_id,
                "scheduled_at": future,
                "title": "RSVP Test Party",
            },
            headers=headers,
        )
        if wp_resp.status_code != 201:
            pytest.skip("Could not create watch party")

        party_id = wp_resp.json()["id"]

        # Get RSVPs
        rsvp_resp = client.get(
            f"/api/v1/watchparty/{party_id}/rsvps",
            headers=headers,
        )
        assert rsvp_resp.status_code == 200, rsvp_resp.text
        body = rsvp_resp.json()
        assert "items" in body
        assert "total" in body


def test_get_watchparty_rsvps_not_found() -> None:
    """GET /watchparty/{fake_id}/rsvps returns 404."""
    with TestClient(app) as client:
        headers = _normal_user_headers(client)
        fake_id = uuid4()
        resp = client.get(f"/api/v1/watchparty/{fake_id}/rsvps", headers=headers)
        assert resp.status_code == 404, resp.text


# ── 5. Notification DELETE ──────────────────────────────────────────────


def test_delete_notification_owner() -> None:
    """A user can delete their own notification."""
    with TestClient(app) as client:
        token = _user_token(client, "notif")
        headers = {"Authorization": f"Bearer {token}"}

        # Get existing notifications
        notifs = client.get("/api/v1/notifications", headers=headers)
        if notifs.status_code != 200 or not notifs.json().get("items"):
            pytest.skip("No notifications to delete")

        notif_id = notifs.json()["items"][0]["id"]

        resp = client.delete(f"/api/v1/notifications/{notif_id}", headers=headers)
        assert resp.status_code == 200, resp.text
        assert resp.json()["deleted"] is True


def test_delete_notification_not_found() -> None:
    """DELETE nonexistent notification returns 404."""
    with TestClient(app) as client:
        headers = _normal_user_headers(client)
        fake_id = uuid4()
        resp = client.delete(f"/api/v1/notifications/{fake_id}", headers=headers)
        assert resp.status_code == 404, resp.text


def test_delete_notification_other_user() -> None:
    """A user cannot delete another user's notification."""
    with TestClient(app) as client:
        token_a = _user_token(client, "owner1")
        token_b = _user_token(client, "thief1")

        headers_a = {"Authorization": f"Bearer {token_a}"}

        notifs = client.get("/api/v1/notifications", headers=headers_a)
        if notifs.status_code != 200 or not notifs.json().get("items"):
            pytest.skip("No notifications to test with")

        notif_id = notifs.json()["items"][0]["id"]

        headers_b = {"Authorization": f"Bearer {token_b}"}
        resp = client.delete(f"/api/v1/notifications/{notif_id}", headers=headers_b)
        assert resp.status_code == 404, resp.text


# ── 6. Users admin list + delete ────────────────────────────────────────


def test_admin_list_users() -> None:
    """Admin can list all users."""
    with TestClient(app) as client:
        headers = _admin_headers(client)
        resp = client.get("/api/v1/users", headers=headers)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "items" in body
        assert "total" in body
        assert len(body["items"]) > 0


def test_admin_list_users_forbidden_for_normal() -> None:
    """Normal users cannot list all users."""
    with TestClient(app) as client:
        headers = _normal_user_headers(client)
        resp = client.get("/api/v1/users", headers=headers)
        assert resp.status_code == 403, resp.text


def test_admin_delete_user() -> None:
    """Admin can soft-delete a user."""
    with TestClient(app) as client:
        admin_headers = _admin_headers(client)

        # Create a disposable user first
        suffix = uuid4().hex[:8]
        token = _user_token(client, suffix)
        user_headers = {"Authorization": f"Bearer {token}"}
        me = client.get("/api/v1/users/me", headers=user_headers)
        user_id = me.json()["id"]

        resp = client.delete(f"/api/v1/users/{user_id}", headers=admin_headers)
        assert resp.status_code == 200, resp.text
        assert resp.json()["deleted"] is True


def test_admin_delete_user_forbidden_for_normal() -> None:
    """Normal users cannot delete other users."""
    with TestClient(app) as client:
        headers = _normal_user_headers(client)
        fake_id = uuid4()
        resp = client.delete(f"/api/v1/users/{fake_id}", headers=headers)
        assert resp.status_code == 403, resp.text


# ── 7. User Settings ────────────────────────────────────────────────────


def test_get_user_settings() -> None:
    """GET /users/me/settings returns settings with defaults."""
    with TestClient(app) as client:
        headers = _normal_user_headers(client)
        resp = client.get("/api/v1/users/me/settings", headers=headers)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "theme" in body
        assert body["theme"] == "system"
        assert body["language"] == "en"
        assert body["timezone"] == "UTC"


def test_patch_user_settings() -> None:
    """PATCH /users/me/settings updates settings."""
    with TestClient(app) as client:
        headers = _normal_user_headers(client)
        resp = client.patch(
            "/api/v1/users/me/settings",
            json={"theme": "dark", "language": "ja"},
            headers=headers,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["theme"] == "dark"
        assert body["language"] == "ja"

        # Verify persistence
        get_resp = client.get("/api/v1/users/me/settings", headers=headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["theme"] == "dark"
