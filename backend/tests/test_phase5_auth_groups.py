"""Phase 5 integration tests: auth + users + groups."""

from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from src.app.main import app
from tests.helpers import register_or_login_as_admin


def _register_and_login(client: TestClient) -> tuple[str, str]:
    suffix = uuid4().hex[:8]
    username = f"phase5_user_{suffix}"
    email = f"phase5_user_{suffix}@example.com"
    password = "password123"

    result = register_or_login_as_admin(client, username, email, password)
    # Login again to get both tokens (access + refresh)
    login = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert login.status_code == 200, login.text
    body = login.json()
    return body["access_token"], body["refresh_token"]


def test_phase5_auth_happy_and_error_paths() -> None:
    with TestClient(app) as client:
        access, refresh = _register_and_login(client)

        bad = client.post("/api/v1/auth/login", json={"username": "nope", "password": "wrongpass"})
        assert bad.status_code == 401

        rr = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
        assert rr.status_code == 200, rr.text
        refreshed = rr.json()
        assert "access_token" in refreshed and "refresh_token" in refreshed

        rr_old = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
        assert rr_old.status_code == 401

        no_auth = client.post("/api/v1/auth/logout", json={"refresh_token": refreshed["refresh_token"]})
        assert no_auth.status_code == 401

        auth_headers = {"Authorization": f"Bearer {access}"}
        out = client.post("/api/v1/auth/logout", json={"refresh_token": refreshed["refresh_token"]}, headers=auth_headers)
        assert out.status_code == 200
        assert out.json()["success"] is True


def test_phase5_users_me_and_groups_flow() -> None:
    with TestClient(app) as client:
        access, _refresh = _register_and_login(client)
        headers = {"Authorization": f"Bearer {access}"}

        me = client.get("/api/v1/users/me", headers=headers)
        assert me.status_code == 200, me.text
        me_body = me.json()
        assert "id" in me_body and "username" in me_body

        patch = client.patch("/api/v1/users/me", json={"display_name": "Updated Name"}, headers=headers)
        assert patch.status_code == 200, patch.text
        assert patch.json()["display_name"] == "Updated Name"

        gc = client.post("/api/v1/groups", json={"name": "My Group", "description": "desc", "is_private": True}, headers=headers)
        assert gc.status_code == 201, gc.text
        group = gc.json()
        group_id = group["id"]
        invite = group["invite_code"]

        gg = client.get(f"/api/v1/groups/{group_id}", headers=headers)
        assert gg.status_code == 200, gg.text

        gm = client.get(f"/api/v1/groups/{group_id}/members", headers=headers)
        assert gm.status_code == 200, gm.text
        assert gm.json()["total"] >= 1

        j = client.post(f"/api/v1/groups/join/{invite}", headers=headers)
        assert j.status_code == 200, j.text
