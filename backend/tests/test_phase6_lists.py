"""Phase 6 integration tests: tracking list endpoints."""

from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from src.app.main import app
from tests.helpers import register_or_login_as_admin


def _register_and_login(client: TestClient) -> str:
    suffix = uuid4().hex[:8]
    username = f"phase6_user_{suffix}"
    email = f"phase6_user_{suffix}@example.com"
    password = "password123"

    result = register_or_login_as_admin(client, username, email, password)
    return result["access_token"]


def _get_first_media_id(client: TestClient, access_token: str) -> str | None:
    """Get the first media entry ID from the database (seeded in conftest)."""
    res = client.get(
        "/api/v1/media/search",
        params={"query": "Naruto", "limit": 1},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if res.status_code == 200:
        items = res.json().get("items", [])
        if items:
            return items[0]["id"]
    return None


def test_phase6_get_my_list_empty_state() -> None:
    with TestClient(app) as client:
        access = _register_and_login(client)
        headers = {"Authorization": f"Bearer {access}"}

        res = client.get("/api/v1/lists/me", headers=headers)
        assert res.status_code == 200, res.text

        body = res.json()
        assert "items" in body
        assert isinstance(body["items"], list)
        assert body["total"] == 0
        assert body["limit"] == 50
        assert body["offset"] == 0


def test_phase6_get_my_list_with_statuses_filter() -> None:
    """Test comma-separated statuses filter on GET /lists/me."""
    with TestClient(app) as client:
        access = _register_and_login(client)
        headers = {"Authorization": f"Bearer {access}"}

        # First, create a list entry in "watching" status
        media_id = _get_first_media_id(client, access)
        if not media_id:
            return  # Skip if no media entry exists

        create_res = client.post(
            "/api/v1/lists",
            json={"media_id": media_id, "status": "watching", "progress": 5},
            headers=headers,
        )
        assert create_res.status_code == 201, create_res.text

        # Fetch with statuses filter = watching,reading
        res = client.get(
            "/api/v1/lists/me",
            params={"statuses": "watching,reading", "limit": 20},
            headers=headers,
        )
        assert res.status_code == 200, res.text
        body = res.json()
        assert len(body["items"]) >= 1
        assert body["items"][0]["status"] == "watching"
        assert body["items"][0]["progress"] == 5

        # Fetch with statuses filter = completed (should be empty)
        res2 = client.get(
            "/api/v1/lists/me",
            params={"statuses": "completed", "limit": 20},
            headers=headers,
        )
        assert res2.status_code == 200, res2.text
        assert len(res2.json()["items"]) == 0


def test_phase6_get_my_list_includes_media() -> None:
    """Test that ListEntryResponse includes nested media object."""
    with TestClient(app) as client:
        access = _register_and_login(client)
        headers = {"Authorization": f"Bearer {access}"}

        media_id = _get_first_media_id(client, access)
        if not media_id:
            return

        # Create list entry
        client.post(
            "/api/v1/lists",
            json={"media_id": media_id, "status": "watching", "progress": 3},
            headers=headers,
        )

        # Verify media field is included
        res = client.get(
            "/api/v1/lists/me",
            params={"statuses": "watching"},
            headers=headers,
        )
        assert res.status_code == 200, res.text
        items = res.json()["items"]
        assert len(items) >= 1
        entry = items[0]
        assert "media" in entry
        assert entry["media"] is not None
        assert entry["media"]["id"] == media_id
        assert "title_romaji" in entry["media"]
        assert "cover_image_medium" in entry["media"]
        assert "episode_count" in entry["media"]
