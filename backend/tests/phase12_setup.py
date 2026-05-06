"""Phase 12 setup/bootstrap tests."""

from __future__ import annotations

from secrets import token_hex

from fastapi.testclient import TestClient

from src.app.main import app


def _login(client: TestClient, username: str, password: str) -> str:
    res = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def test_phase12_setup_status_true_before_bootstrap() -> None:
    with TestClient(app) as client:
        res = client.get("/api/v1/setup/status")
        assert res.status_code == 200, res.text
        assert res.json()["setup_required"] is True


def test_phase12_bootstrap_admin_once_then_locked() -> None:
    with TestClient(app) as client:
        suffix = token_hex(4)
        payload = {
            "username": f"admin_{suffix}",
            "email": f"admin_{suffix}@example.com",
            "password": "password123",
        }

        first = client.post("/api/v1/setup/bootstrap-admin", json=payload)
        assert first.status_code == 201, first.text

        second = client.post("/api/v1/setup/bootstrap-admin", json=payload)
        assert second.status_code == 409

        status = client.get("/api/v1/setup/status")
        assert status.status_code == 200
        assert status.json()["setup_required"] is False


def test_phase12_public_register_disabled_after_bootstrap() -> None:
    with TestClient(app) as client:
        suffix = token_hex(4)
        admin_payload = {
            "username": f"boot_{suffix}",
            "email": f"boot_{suffix}@example.com",
            "password": "password123",
        }
        boot = client.post("/api/v1/setup/bootstrap-admin", json=admin_payload)
        if boot.status_code not in (201, 409):
            assert boot.status_code == 201, boot.text

        res = client.post(
            "/api/v1/auth/register",
            json={"username": f"u_{suffix}", "email": f"u_{suffix}@example.com", "password": "password123"},
        )
        assert res.status_code == 403


def test_phase12_admin_can_create_user_non_admin_cannot() -> None:
    with TestClient(app) as client:
        suffix = token_hex(4)
        admin_username = f"root_{suffix}"
        admin_password = "password123"
        boot_payload = {
            "username": admin_username,
            "email": f"{admin_username}@example.com",
            "password": admin_password,
        }
        boot = client.post("/api/v1/setup/bootstrap-admin", json=boot_payload)
        if boot.status_code not in (201, 409):
            assert boot.status_code == 201, boot.text

        admin_token = _login(client, admin_username, admin_password)
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
