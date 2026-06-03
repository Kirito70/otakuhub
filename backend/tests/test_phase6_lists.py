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
