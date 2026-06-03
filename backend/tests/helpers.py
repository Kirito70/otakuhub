"""Shared test helpers for integration tests.

All integration tests run in the same process against a single in-memory
SQLite database.  The conftest's ``pytest_sessionstart`` bootstraps an admin
user with these credentials so that any test that needs to create users after
public registration is locked can login as admin and use the admin user
creation endpoint.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

# Matches the admin created in conftest.pytest_sessionstart
ADMIN_USERNAME = "test_root_admin"
ADMIN_PASSWORD = "TestRoot123!"


def register_or_login_as_admin(
    client: TestClient, username: str, email: str, password: str
) -> dict[str, str]:
    """Try to register a user; if public registration is locked, create the
    user via the admin endpoint and return the user dict (must have 'id').

    Returns ``dict`` with ``user_id`` and ``access_token`` keys.
    """
    r = client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    if r.status_code == 201:
        user_id = r.json()["id"]
        token = _login(client, username, password)
        return {"user_id": user_id, "access_token": token}

    # Registration locked — create via admin endpoint
    login = client.post(
        "/api/v1/auth/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert login.status_code == 200, (
        f"Admin login failed: {login.status_code} {login.text}. "
        "Is conftest pytest_sessionstart running?"
    )
    admin_token = login.json()["access_token"]

    created = client.post(
        "/api/v1/users",
        json={"username": username, "email": email, "password": password},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert created.status_code == 201, created.text

    user_token = _login(client, username, password)
    return {"user_id": created.json()["id"], "access_token": user_token}


def _login(client: TestClient, username: str, password: str) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]
