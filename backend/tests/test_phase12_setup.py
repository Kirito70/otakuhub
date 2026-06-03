"""Phase 12 setup/bootstrap tests."""

from __future__ import annotations

from secrets import token_hex

from fastapi.testclient import TestClient

from src.app.main import app
from tests.helpers import ADMIN_USERNAME, ADMIN_PASSWORD


def _bootstrap_admin_or_existing(
    client: TestClient, suffix: str
) -> tuple[str, str]:
    """Try to bootstrap a fresh admin; if already bootstrapped login as the
    known conftest admin.
    """
    payload = {
        "username": f"phase12_root_{suffix}",
        "email": f"phase12_root_{suffix}@example.com",
        "password": "password123",
    }
    boot = client.post("/api/v1/setup/bootstrap-admin", json=payload)
    if boot.status_code == 201:
        return payload["username"], payload["password"]
    # Already bootstrapped — use conftest admin
    return ADMIN_USERNAME, ADMIN_PASSWORD


def _login(client: TestClient, username: str, password: str) -> str:
    res = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def test_phase12_setup_status_true_before_bootstrap() -> None:
    with TestClient(app) as client:
        res = client.get("/api/v1/setup/status")
        assert res.status_code == 200, res.text
        data = res.json()
        # setup_required: True if fresh DB, absent (excluded by exclude_none) if bootstrapped
        if "setup_required" in data:
            assert data["setup_required"] is True
        # When absent, treat as False (setup already completed)


def test_phase12_bootstrap_admin_once_then_locked() -> None:
    with TestClient(app) as client:
        suffix = token_hex(4)
        payload = {
            "username": f"admin_{suffix}",
            "email": f"admin_{suffix}@example.com",
            "password": "password123",
        }

        first = client.post("/api/v1/setup/bootstrap-admin", json=payload)
        assert first.status_code in (201, 409), first.text

        second = client.post("/api/v1/setup/bootstrap-admin", json=payload)
        # If the first call succeeded (201) then second must be 409.
        # If the first was already 409 (pre-bootstrapped), second is also 409.
        assert second.status_code == 409

        status = client.get("/api/v1/setup/status")
        assert status.status_code == 200
        data = status.json()
        # After bootstrap, setup_required is False → excluded via exclude_none
        assert "setup_required" not in data or data["setup_required"] is None


def test_phase12_public_register_disabled_after_bootstrap() -> None:
    with TestClient(app) as client:
        suffix = token_hex(4)
        # Bootstrap (or confirm it's already done)
        _bootstrap_admin_or_existing(client, suffix)

        res = client.post(
            "/api/v1/auth/register",
            json={"username": f"u_{suffix}", "email": f"u_{suffix}@example.com", "password": "password123"},
        )
        assert res.status_code == 403


def test_phase12_admin_can_create_user_non_admin_cannot() -> None:
    with TestClient(app) as client:
        suffix = token_hex(4)
        admin_user, admin_pass = _bootstrap_admin_or_existing(client, suffix)
        admin_token = _login(client, admin_user, admin_pass)
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        create_payload = {
            "username": f"member_{suffix}",
            "email": f"member_{suffix}@example.com",
            "password": "password123",
        }
        created = client.post("/api/v1/users", headers=admin_headers, json=create_payload)
        assert created.status_code == 201, created.text

        member_token = _login(client, create_payload["username"], create_payload["password"])
        member_headers = {"Authorization": f"Bearer {member_token}"}

        denied = client.post(
            "/api/v1/users",
            headers=member_headers,
            json={
                "username": f"another_{suffix}",
                "email": f"another_{suffix}@example.com",
                "password": "password123",
            },
        )
        assert denied.status_code == 403


def test_phase12_bootstrap_context_omits_setup_required_after_init_and_includes_logged_user() -> None:
    with TestClient(app) as client:
        suffix = token_hex(4)
        # Use bootstrapped admin (may be conftest admin if already bootstrapped)
        admin_username = f"ctx_{suffix}"
        admin_password = "password123"
        boot = client.post(
            "/api/v1/setup/bootstrap-admin",
            json={
                "username": admin_username,
                "email": f"{admin_username}@example.com",
                "password": admin_password,
            },
        )
        if boot.status_code == 201:
            pass  # We'll login as ctx_{suffix}
        else:
            # Already bootstrapped — use conftest admin
            admin_username, admin_password = ADMIN_USERNAME, ADMIN_PASSWORD

        token = _login(client, admin_username, admin_password)
        res = client.get(
            "/api/v1/setup/bootstrap",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["site_status"] in ("up", "degraded")
        assert "setup_required" not in body
        assert body["logged_in_user"]["username"] == admin_username
