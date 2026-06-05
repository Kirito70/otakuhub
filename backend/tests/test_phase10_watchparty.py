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
