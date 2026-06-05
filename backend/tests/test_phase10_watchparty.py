"""Phase 10 integration tests: watch party endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta, UTC
from secrets import token_hex
from uuid import uuid4

from fastapi.testclient import TestClient

from src.app.main import app
from tests.helpers import register_or_login_as_admin


def _register_and_login(client: TestClient, prefix: str) -> dict[str, str]:
    suffix = token_hex(4)
    username = f"{prefix}_{suffix}"
    email = f"{username}@example.com"
    password = "password123"

    return register_or_login_as_admin(client, username, email, password)


def test_phase10_create_watchparty_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/watchparty",
            json={
                "group_id": str(uuid4()),
                "media_id": str(uuid4()),
                "scheduled_at": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
            },
        )
        assert res.status_code == 401


def test_phase10_create_watchparty_requires_group_membership() -> None:
    with TestClient(app) as client:
        owner = _register_and_login(client, "ownerwp")
        outsider = _register_and_login(client, "outsiderwp")

        owner_headers = {"Authorization": f"Bearer {owner['access_token']}"}
        outsider_headers = {"Authorization": f"Bearer {outsider['access_token']}"}

        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Watch Group", "description": "phase10", "is_private": True},
            headers=owner_headers,
        )
        assert group_create.status_code == 201, group_create.text
        group_id = group_create.json()["id"]

        res = client.post(
            "/api/v1/watchparty",
            json={
                "group_id": group_id,
                "media_id": str(uuid4()),
                "scheduled_at": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
                "title": "Friday Party",
            },
            headers=outsider_headers,
        )
        assert res.status_code == 403, res.text


def test_phase10_create_watchparty_returns_400_when_media_not_seeded() -> None:
    with TestClient(app) as client:
        owner = _register_and_login(client, "ownerwp2")
        member = _register_and_login(client, "memberwp2")

        owner_headers = {"Authorization": f"Bearer {owner['access_token']}"}
        member_headers = {"Authorization": f"Bearer {member['access_token']}"}

        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Watch Group 2", "description": "phase10", "is_private": True},
            headers=owner_headers,
        )
        assert group_create.status_code == 201, group_create.text
        invite_code = group_create.json()["invite_code"]
        group_id = group_create.json()["id"]

        join_member = client.post(f"/api/v1/groups/join/{invite_code}", headers=member_headers)
        assert join_member.status_code == 200, join_member.text

        res = client.post(
            "/api/v1/watchparty",
            json={
                "group_id": group_id,
                "media_id": str(uuid4()),
                "scheduled_at": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
                "title": "Seed pending party",
                "episode_number": 1,
            },
            headers=member_headers,
        )
        assert res.status_code == 400, res.text


def test_phase10_get_watchparty_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.get("/api/v1/watchparty")
        assert res.status_code == 401


def test_phase10_get_watchparty_returns_empty_for_member_group_scope() -> None:
    with TestClient(app) as client:
        owner = _register_and_login(client, "ownerwp3")
        member = _register_and_login(client, "memberwp3")

        owner_headers = {"Authorization": f"Bearer {owner['access_token']}"}
        member_headers = {"Authorization": f"Bearer {member['access_token']}"}

        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Watch Group 3", "description": "phase10", "is_private": True},
            headers=owner_headers,
        )
        assert group_create.status_code == 201, group_create.text
        invite_code = group_create.json()["invite_code"]
        group_id = group_create.json()["id"]

        join_member = client.post(f"/api/v1/groups/join/{invite_code}", headers=member_headers)
        assert join_member.status_code == 200, join_member.text

        res = client.get(f"/api/v1/watchparty?group_id={group_id}&limit=20&offset=0", headers=member_headers)
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["items"] == []
        assert body["total"] == 0
        assert body["limit"] == 20
        assert body["offset"] == 0


def test_phase10_get_watchparty_forbidden_for_non_member_group_scope() -> None:
    with TestClient(app) as client:
        owner = _register_and_login(client, "ownerwp4")
        outsider = _register_and_login(client, "outsiderwp4")

        owner_headers = {"Authorization": f"Bearer {owner['access_token']}"}
        outsider_headers = {"Authorization": f"Bearer {outsider['access_token']}"}

        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Watch Group 4", "description": "phase10", "is_private": True},
            headers=owner_headers,
        )
        assert group_create.status_code == 201, group_create.text
        group_id = group_create.json()["id"]

        res = client.get(f"/api/v1/watchparty?group_id={group_id}", headers=outsider_headers)
        assert res.status_code == 403, res.text


def test_phase10_watchparty_rsvp_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.post(f"/api/v1/watchparty/{uuid4()}/rsvp", json={"status": "attending"})
        assert res.status_code == 401


def test_phase10_watchparty_rsvp_returns_404_for_missing_party() -> None:
    with TestClient(app) as client:
        user = _register_and_login(client, "rsvpuser")
        headers = {"Authorization": f"Bearer {user['access_token']}"}

        res = client.post(
            f"/api/v1/watchparty/{uuid4()}/rsvp",
            json={"status": "attending"},
            headers=headers,
        )
        assert res.status_code == 404, res.text


# --- Watch Party Detail (GET /{party_id}) ---


def _get_seeded_media_id(client: TestClient, auth_header: dict) -> str:
    """Return a media ID from the seeded test data."""
    res = client.get("/api/v1/media/search?query=Naruto&limit=1", headers=auth_header)
    assert res.status_code == 200, res.text
    data = res.json()
    # The search response may be nested under 'items' or direct list
    if isinstance(data, list):
        assert len(data) > 0, "No seeded media found"
        return data[0]["id"]
    items = data.get("items") or data.get("results") or data.get("data") or []
    assert len(items) > 0, f"No seeded media found. Response: {data}"
    return items[0]["id"]


def test_phase10_watchparty_detail_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.get(f"/api/v1/watchparty/{uuid4()}")
        assert res.status_code == 401


def test_phase10_watchparty_detail_returns_404_for_missing_party() -> None:
    with TestClient(app) as client:
        user = _register_and_login(client, "detail404")
        headers = {"Authorization": f"Bearer {user['access_token']}"}

        res = client.get(f"/api/v1/watchparty/{uuid4()}", headers=headers)
        assert res.status_code == 404, res.text


def test_phase10_watchparty_detail_returns_403_for_non_member() -> None:
    with TestClient(app) as client:
        owner = _register_and_login(client, "detailowner")
        outsider = _register_and_login(client, "detailoutsider")

        owner_headers = {"Authorization": f"Bearer {owner['access_token']}"}
        outsider_headers = {"Authorization": f"Bearer {outsider['access_token']}"}

        media_id = _get_seeded_media_id(client, owner_headers)

        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Detail Group", "description": "detail403", "is_private": True},
            headers=owner_headers,
        )
        assert group_create.status_code == 201, group_create.text
        group_id = group_create.json()["id"]

        party_create = client.post(
            "/api/v1/watchparty",
            json={
                "group_id": group_id,
                "media_id": media_id,
                "scheduled_at": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
                "title": "Detail Test Party",
            },
            headers=owner_headers,
        )
        assert party_create.status_code == 201, party_create.text
        party_id = party_create.json()["id"]

        # Outsider tries to get detail
        res = client.get(f"/api/v1/watchparty/{party_id}", headers=outsider_headers)
        assert res.status_code == 403, res.text


def test_phase10_watchparty_detail_success() -> None:
    with TestClient(app) as client:
        host = _register_and_login(client, "detailhost")
        member = _register_and_login(client, "detailmember")

        host_headers = {"Authorization": f"Bearer {host['access_token']}"}
        member_headers = {"Authorization": f"Bearer {member['access_token']}"}

        media_id = _get_seeded_media_id(client, host_headers)

        # Create group
        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Detail Success Group", "description": "detail200", "is_private": True},
            headers=host_headers,
        )
        assert group_create.status_code == 201, group_create.text
        group_id = group_create.json()["id"]
        invite_code = group_create.json()["invite_code"]

        # Join member
        join_member = client.post(f"/api/v1/groups/join/{invite_code}", headers=member_headers)
        assert join_member.status_code == 200, join_member.text

        # Create watch party
        scheduled = (datetime.now(UTC) + timedelta(days=1)).isoformat()
        party_create = client.post(
            "/api/v1/watchparty",
            json={
                "group_id": group_id,
                "media_id": media_id,
                "scheduled_at": scheduled,
                "title": "Party Detail Success",
                "episode_number": 5,
                "stream_url": "https://example.com/stream",
                "sync_url": "https://example.com/sync",
                "notes": "Test notes",
            },
            headers=host_headers,
        )
        assert party_create.status_code == 201, party_create.text
        party_id = party_create.json()["id"]

        # Member RSVPs as attending
        rsvp_res = client.post(
            f"/api/v1/watchparty/{party_id}/rsvp",
            json={"status": "attending"},
            headers=member_headers,
        )
        assert rsvp_res.status_code == 200, rsvp_res.text

        # GET detail as host
        res = client.get(f"/api/v1/watchparty/{party_id}", headers=host_headers)
        assert res.status_code == 200, res.text
        body = res.json()

        # Verify party fields
        assert body["id"] == party_id
        assert body["group_id"] == group_id
        assert body["host_user_id"] == host["user_id"]
        assert body["title"] == "Party Detail Success"
        assert body["episode_number"] == 5
        assert body["stream_url"] == "https://example.com/stream"
        assert body["sync_url"] == "https://example.com/sync"
        assert body["notes"] == "Test notes"
        assert body["status"] == "scheduled"

        # Verify media info
        assert body["media_title"] is not None
        assert "Naruto" in body["media_title"]

        # Verify host info
        assert body["host_username"] is not None

        # Verify RSVP summary
        assert body["rsvp_summary"] is not None
        assert body["rsvp_summary"]["attending"] >= 1
        assert body["attendee_count"] >= 1


# --- Watch Party Past (GET /past) ---


def test_phase10_watchparty_past_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.get("/api/v1/watchparty/past")
        assert res.status_code == 401


def test_phase10_watchparty_past_returns_empty_for_no_past_parties() -> None:
    with TestClient(app) as client:
        owner = _register_and_login(client, "pastempty")
        member = _register_and_login(client, "pastemptymem")

        owner_headers = {"Authorization": f"Bearer {owner['access_token']}"}
        member_headers = {"Authorization": f"Bearer {member['access_token']}"}

        media_id = _get_seeded_media_id(client, owner_headers)

        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Past Empty Group", "description": "pastempty", "is_private": True},
            headers=owner_headers,
        )
        assert group_create.status_code == 201, group_create.text
        group_id = group_create.json()["id"]
        invite_code = group_create.json()["invite_code"]

        join_member = client.post(f"/api/v1/groups/join/{invite_code}", headers=member_headers)
        assert join_member.status_code == 200, join_member.text

        # Create a future party (should NOT appear in past)
        future_scheduled = (datetime.now(UTC) + timedelta(days=1)).isoformat()
        party_create = client.post(
            "/api/v1/watchparty",
            json={
                "group_id": group_id,
                "media_id": media_id,
                "scheduled_at": future_scheduled,
                "title": "Future Party",
            },
            headers=owner_headers,
        )
        assert party_create.status_code == 201, party_create.text

        # Get past parties — should be empty
        res = client.get("/api/v1/watchparty/past?limit=20&offset=0", headers=member_headers)
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["items"] == []
        assert body["total"] == 0


def test_phase10_watchparty_past_returns_past_parties() -> None:
    with TestClient(app) as client:
        owner = _register_and_login(client, "pasthost")
        member = _register_and_login(client, "pastmem")

        owner_headers = {"Authorization": f"Bearer {owner['access_token']}"}
        member_headers = {"Authorization": f"Bearer {member['access_token']}"}

        media_id = _get_seeded_media_id(client, owner_headers)

        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Past Party Group", "description": "pastparty", "is_private": True},
            headers=owner_headers,
        )
        assert group_create.status_code == 201, group_create.text
        group_id = group_create.json()["id"]
        invite_code = group_create.json()["invite_code"]

        join_member = client.post(f"/api/v1/groups/join/{invite_code}", headers=member_headers)
        assert join_member.status_code == 200, join_member.text

        # Create a past party (scheduled yesterday) — should appear in past
        past_scheduled = (datetime.now(UTC) - timedelta(days=1)).isoformat()
        party_create = client.post(
            "/api/v1/watchparty",
            json={
                "group_id": group_id,
                "media_id": media_id,
                "scheduled_at": past_scheduled,
                "title": "Past Party",
            },
            headers=owner_headers,
        )
        assert party_create.status_code == 201, party_create.text
        past_party_id = party_create.json()["id"]

        # Get past parties — should include the past party
        res = client.get("/api/v1/watchparty/past?limit=20&offset=0", headers=member_headers)
        assert res.status_code == 200, res.text
        body = res.json()
        assert len(body["items"]) >= 1
        assert body["total"] >= 1
        party_ids = [item["id"] for item in body["items"]]
        assert past_party_id in party_ids


def test_phase10_watchparty_past_returns_403_for_non_member_group_scope() -> None:
    with TestClient(app) as client:
        owner = _register_and_login(client, "pastowner2")
        outsider = _register_and_login(client, "pastoutsider2")

        owner_headers = {"Authorization": f"Bearer {owner['access_token']}"}

        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Past Group 2", "description": "past403", "is_private": True},
            headers=owner_headers,
        )
        assert group_create.status_code == 201, group_create.text
        group_id = group_create.json()["id"]

        outsider_headers = {"Authorization": f"Bearer {outsider['access_token']}"}
        res = client.get(f"/api/v1/watchparty/past?group_id={group_id}", headers=outsider_headers)
        assert res.status_code == 403, res.text


# --- Watch Party Update (PATCH /{party_id}) ---


def test_phase10_watchparty_update_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.patch(f"/api/v1/watchparty/{uuid4()}", json={"title": "x"})
        assert res.status_code == 401


def test_phase10_watchparty_update_updates_party() -> None:
    with TestClient(app) as client:
        host = _register_and_login(client, "wpartyupd_host")
        member = _register_and_login(client, "wpartyupd_mem")
        host_h = {"Authorization": f"Bearer {host['access_token']}"}
        member_h = {"Authorization": f"Bearer {member['access_token']}"}

        media_id = _get_seeded_media_id(client, host_h)

        g_res = client.post(
            "/api/v1/groups",
            json={"name": "WpUpdGroup", "description": "", "is_private": False},
            headers=host_h,
        )
        assert g_res.status_code == 201, g_res.text
        group_id = g_res.json()["id"]

        future = (datetime.now(UTC) + timedelta(days=1)).isoformat()
        p_res = client.post(
            "/api/v1/watchparty",
            json={"group_id": group_id, "media_id": media_id, "scheduled_at": future, "title": "Original"},
            headers=host_h,
        )
        assert p_res.status_code == 201, p_res.text
        party_id = p_res.json()["id"]

        # Update
        upd = client.patch(
            f"/api/v1/watchparty/{party_id}",
            json={"title": "Updated Title", "notes": "New notes"},
            headers=host_h,
        )
        assert upd.status_code == 200, upd.text
        body = upd.json()
        assert body["title"] == "Updated Title"
        assert body["notes"] == "New notes"


def test_phase10_watchparty_non_host_cannot_update() -> None:
    with TestClient(app) as client:
        host = _register_and_login(client, "wpnoupd_host")
        member = _register_and_login(client, "wpnoupd_mem")
        host_h = {"Authorization": f"Bearer {host['access_token']}"}
        member_h = {"Authorization": f"Bearer {member['access_token']}"}

        media_id = _get_seeded_media_id(client, host_h)

        g_res = client.post(
            "/api/v1/groups",
            json={"name": "WpNoUpdGroup", "description": "", "is_private": False},
            headers=host_h,
        )
        assert g_res.status_code == 201, g_res.text
        group_id = g_res.json()["id"]
        invite = g_res.json()["invite_code"]

        client.post(f"/api/v1/groups/join/{invite}", headers=member_h)

        future = (datetime.now(UTC) + timedelta(days=1)).isoformat()
        p_res = client.post(
            "/api/v1/watchparty",
            json={"group_id": group_id, "media_id": media_id, "scheduled_at": future, "title": "Original"},
            headers=host_h,
        )
        assert p_res.status_code == 201, p_res.text
        party_id = p_res.json()["id"]

        # Non-host tries to update
        upd = client.patch(
            f"/api/v1/watchparty/{party_id}",
            json={"title": "Hacked"},
            headers=member_h,
        )
        assert upd.status_code == 403, upd.text


def test_phase10_watchparty_delete_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.delete(f"/api/v1/watchparty/{uuid4()}")
        assert res.status_code == 401


def test_phase10_watchparty_delete_soft_deletes() -> None:
    with TestClient(app) as client:
        host = _register_and_login(client, "wpdel_host")
        host_h = {"Authorization": f"Bearer {host['access_token']}"}

        media_id = _get_seeded_media_id(client, host_h)

        g_res = client.post(
            "/api/v1/groups",
            json={"name": "WpDelGroup", "description": "", "is_private": False},
            headers=host_h,
        )
        assert g_res.status_code == 201, g_res.text
        group_id = g_res.json()["id"]

        future = (datetime.now(UTC) + timedelta(days=1)).isoformat()
        p_res = client.post(
            "/api/v1/watchparty",
            json={"group_id": group_id, "media_id": media_id, "scheduled_at": future, "title": "ToDelete"},
            headers=host_h,
        )
        assert p_res.status_code == 201, p_res.text
        party_id = p_res.json()["id"]

        del_res = client.delete(f"/api/v1/watchparty/{party_id}", headers=host_h)
        assert del_res.status_code == 204

        get_res = client.get(f"/api/v1/watchparty/{party_id}", headers=host_h)
        assert get_res.status_code == 404


def test_phase10_watchparty_non_host_cannot_delete() -> None:
    with TestClient(app) as client:
        host = _register_and_login(client, "wpnodelete_host")
        member = _register_and_login(client, "wpnodelete_mem")
        host_h = {"Authorization": f"Bearer {host['access_token']}"}
        member_h = {"Authorization": f"Bearer {member['access_token']}"}

        media_id = _get_seeded_media_id(client, host_h)

        g_res = client.post(
            "/api/v1/groups",
            json={"name": "WpNoDelGroup", "description": "", "is_private": False},
            headers=host_h,
        )
        assert g_res.status_code == 201, g_res.text
        group_id = g_res.json()["id"]
        invite = g_res.json()["invite_code"]

        client.post(f"/api/v1/groups/join/{invite}", headers=member_h)

        future = (datetime.now(UTC) + timedelta(days=1)).isoformat()
        p_res = client.post(
            "/api/v1/watchparty",
            json={"group_id": group_id, "media_id": media_id, "scheduled_at": future, "title": "ToDelete"},
            headers=host_h,
        )
        assert p_res.status_code == 201, p_res.text
        party_id = p_res.json()["id"]

        del_res = client.delete(f"/api/v1/watchparty/{party_id}", headers=member_h)
        assert del_res.status_code == 403
