"""Phase 10 integration tests: watch party endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta, UTC
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
