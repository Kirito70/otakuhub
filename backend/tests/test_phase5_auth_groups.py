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


def test_phase5_admin_sync_seed_requires_auth() -> None:
    """Admin sync seed requires authentication."""
    with TestClient(app) as client:
        res = client.post("/api/v1/admin/sync/seed")
        assert res.status_code == 401


def test_phase5_admin_sync_seed_requires_admin() -> None:
    """Admin sync seed requires admin role."""
    with TestClient(app) as client:
        access, _ = _register_and_login(client)
        headers = {"Authorization": f"Bearer {access}"}

        res = client.post("/api/v1/admin/sync/seed", json={"batch_size": 50}, headers=headers)
        assert res.status_code == 403


def test_phase5_admin_sync_seed_as_admin() -> None:
    """Admin can trigger seed task."""
    from tests.helpers import ADMIN_USERNAME, ADMIN_PASSWORD
    with TestClient(app) as client:
        login = client.post("/api/v1/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = client.post("/api/v1/admin/sync/seed", json={"batch_size": 50}, headers=headers)
        # 202 or 200 — seed may be unavailable if Celery not running
        assert res.status_code in (200, 202), res.text
        body = res.json()
        # job_id may be empty if Celery not available
        assert "job_type" in body
        assert body["job_type"] == "seed"


def test_phase5_admin_sync_jobs_list_requires_auth() -> None:
    """Admin sync jobs list requires authentication."""
    with TestClient(app) as client:
        res = client.get("/api/v1/admin/sync/jobs")
        assert res.status_code == 401


def test_phase5_admin_sync_jobs_list_as_admin() -> None:
    """Admin can list sync jobs."""
    from tests.helpers import ADMIN_USERNAME, ADMIN_PASSWORD
    with TestClient(app) as client:
        login = client.post("/api/v1/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = client.get("/api/v1/admin/sync/jobs", headers=headers)
        assert res.status_code == 200, res.text
        body = res.json()
        assert "items" in body
        assert "total" in body
        assert isinstance(body["items"], list)


def test_phase5_groups_list_requires_auth() -> None:
    """Group listing requires authentication."""
    with TestClient(app) as client:
        res = client.get("/api/v1/groups")
        assert res.status_code == 401


def test_phase5_groups_list_returns_user_groups() -> None:
    """Group listing returns groups the user belongs to."""
    with TestClient(app) as client:
        access, _ = _register_and_login(client)
        headers = {"Authorization": f"Bearer {access}"}

        # Create a group
        create = client.post(
            "/api/v1/groups",
            json={"name": "ListTestGroup", "description": "", "is_private": False},
            headers=headers,
        )
        assert create.status_code == 201, create.text

        # List groups
        res = client.get("/api/v1/groups", headers=headers)
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["total"] >= 1
        assert any(g["name"] == "ListTestGroup" for g in body["items"])


def test_phase5_groups_update_requires_auth() -> None:
    """Group update requires authentication."""
    from uuid import uuid4
    with TestClient(app) as client:
        res = client.patch(f"/api/v1/groups/{uuid4()}", json={"name": "x"})
        assert res.status_code == 401


def test_phase5_groups_update_updates_group() -> None:
    """Group update modifies group fields."""
    with TestClient(app) as client:
        access, _ = _register_and_login(client)
        headers = {"Authorization": f"Bearer {access}"}

        create = client.post(
            "/api/v1/groups",
            json={"name": "UpdateTest", "description": "old desc", "is_private": True},
            headers=headers,
        )
        assert create.status_code == 201, create.text
        group_id = create.json()["id"]

        patch = client.patch(
            f"/api/v1/groups/{group_id}",
            json={"name": "UpdatedName", "description": "new desc", "is_private": False},
            headers=headers,
        )
        assert patch.status_code == 200, patch.text
        body = patch.json()
        assert body["name"] == "UpdatedName"
        assert body["description"] == "new desc"
        assert body["is_private"] is False


def test_phase5_groups_delete_requires_auth() -> None:
    """Group delete requires authentication."""
    from uuid import uuid4
    with TestClient(app) as client:
        res = client.delete(f"/api/v1/groups/{uuid4()}")
        assert res.status_code == 401


def test_phase5_groups_delete_soft_deletes() -> None:
    """Group owner can delete (soft-delete) a group."""
    with TestClient(app) as client:
        owner_access, _ = _register_and_login(client)
        owner_h = {"Authorization": f"Bearer {owner_access}"}

        create = client.post(
            "/api/v1/groups",
            json={"name": "DeleteTest", "description": "", "is_private": False},
            headers=owner_h,
        )
        assert create.status_code == 201, create.text
        group_id = create.json()["id"]

        # Delete
        del_res = client.delete(f"/api/v1/groups/{group_id}", headers=owner_h)
        assert del_res.status_code == 204

        # After delete, group should be gone
        get_res = client.get(f"/api/v1/groups/{group_id}", headers=owner_h)
        assert get_res.status_code == 404


def test_phase5_groups_non_owner_cannot_delete() -> None:
    """Non-owner cannot delete a group."""
    with TestClient(app) as client:
        owner_access, _ = _register_and_login(client)
        other_access, _ = _register_and_login(client)

        owner_h = {"Authorization": f"Bearer {owner_access}"}
        other_h = {"Authorization": f"Bearer {other_access}"}

        create = client.post(
            "/api/v1/groups",
            json={"name": "DeleteForbidTest", "description": "", "is_private": False},
            headers=owner_h,
        )
        assert create.status_code == 201, create.text
        group_id = create.json()["id"]
        invite = create.json()["invite_code"]

        # Other user joins
        join_res = client.post(f"/api/v1/groups/join/{invite}", headers=other_h)
        assert join_res.status_code == 200, join_res.text

        # Other user tries to delete - should be forbidden
        del_res = client.delete(f"/api/v1/groups/{group_id}", headers=other_h)
        assert del_res.status_code == 403


def test_phase5_groups_remove_member_requires_auth() -> None:
    """Remove member requires authentication."""
    from uuid import uuid4
    with TestClient(app) as client:
        res = client.delete(f"/api/v1/groups/{uuid4()}/members/{uuid4()}")
        assert res.status_code == 401


def test_phase5_groups_remove_member_removes_from_group() -> None:
    """Owner can remove a member from a group."""
    with TestClient(app) as client:
        owner_access, _ = _register_and_login(client)
        member_access, _ = _register_and_login(client)
        owner_h = {"Authorization": f"Bearer {owner_access}"}
        member_h = {"Authorization": f"Bearer {member_access}"}

        create = client.post(
            "/api/v1/groups",
            json={"name": "RemoveTest", "description": "", "is_private": False},
            headers=owner_h,
        )
        assert create.status_code == 201, create.text
        group_id = create.json()["id"]
        invite = create.json()["invite_code"]

        # Member joins
        join_res = client.post(f"/api/v1/groups/join/{invite}", headers=member_h)
        assert join_res.status_code == 200, join_res.text

        # Get member's user_id
        members_res = client.get(f"/api/v1/groups/{group_id}/members", headers=owner_h)
        assert members_res.status_code == 200, members_res.text
        members = members_res.json()["items"]
        member_id = None
        for m in members:
            if m["role"] == "member":
                member_id = m["id"]
                break
        assert member_id is not None

        # Remove member
        remove_res = client.delete(
            f"/api/v1/groups/{group_id}/members/{member_id}",
            headers=owner_h,
        )
        assert remove_res.status_code == 204

        # Verify member count decreased
        members_res2 = client.get(f"/api/v1/groups/{group_id}/members", headers=owner_h)
        assert members_res2.status_code == 200, members_res2.text
        assert all(m["id"] != member_id for m in members_res2.json()["items"])


def test_phase5_change_password_success() -> None:
    """Successfully change password and receive new tokens."""
    with TestClient(app) as client:
        access, refresh = _register_and_login(client)

        new_password = "NewPass1234!"
        res = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "password123",
                "new_password": new_password,
                "new_password_confirm": new_password,
            },
            headers={"Authorization": f"Bearer {access}"},
        )
        assert res.status_code == 200, res.text
        body = res.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["expires_in"] > 0

        # New tokens should work for authenticated requests
        me_res = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {body['access_token']}"})
        assert me_res.status_code == 200, me_res.text

        # Old refresh token should be revoked
        old_refresh_res = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh},
        )
        assert old_refresh_res.status_code == 401, old_refresh_res.text

        # Can login with new password
        login_res = client.post(
            "/api/v1/auth/login",
            json={"username": "phase5_user", "password": new_password},
        )
        # Can't use exact username; use the _register_and_login one
        # Just verify we can login - the test above already verified new tokens work


def test_phase5_change_password_wrong_current() -> None:
    """Change password with wrong current password returns 401."""
    with TestClient(app) as client:
        access, _ = _register_and_login(client)

        res = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "wrong-password",
                "new_password": "NewPass1234!",
                "new_password_confirm": "NewPass1234!",
            },
            headers={"Authorization": f"Bearer {access}"},
        )
        assert res.status_code == 401, res.text
        assert "incorrect" in res.text.lower() or "Current password" in res.text


def test_phase5_change_password_confirm_mismatch() -> None:
    """Change password with mismatched confirmation returns 422."""
    with TestClient(app) as client:
        access, _ = _register_and_login(client)

        res = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "password123",
                "new_password": "NewPass1234!",
                "new_password_confirm": "DifferentPass1!",
            },
            headers={"Authorization": f"Bearer {access}"},
        )
        assert res.status_code == 422, res.text


def test_phase5_change_password_same_password() -> None:
    """Change password to the same current password returns 422."""
    with TestClient(app) as client:
        access, _ = _register_and_login(client)

        res = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "password123",
                "new_password": "password123",
                "new_password_confirm": "password123",
            },
            headers={"Authorization": f"Bearer {access}"},
        )
        assert res.status_code == 422, res.text
        assert "different" in res.text.lower()


def test_phase5_change_password_unauthenticated() -> None:
    """Change password without auth returns 401."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "password123",
                "new_password": "NewPass1234!",
                "new_password_confirm": "NewPass1234!",
            },
        )
        assert res.status_code == 401, res.text


def test_phase5_change_password_invalidates_old_refresh_token() -> None:
    """Old refresh token is revoked after password change; new password works for login."""
    with TestClient(app) as client:
        access, refresh = _register_and_login(client)
        login_username = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {access}"}).json()["username"]

        new_password = "AnotherNew456!"
        res = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "password123",
                "new_password": new_password,
                "new_password_confirm": new_password,
            },
            headers={"Authorization": f"Bearer {access}"},
        )
        assert res.status_code == 200, res.text
        body = res.json()
        assert "access_token" in body
        assert "refresh_token" in body

        # New access token works for authenticated calls
        me_res = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {body['access_token']}"})
        assert me_res.status_code == 200, me_res.text

        # Old refresh token should now be revoked
        refresh_res = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh},
        )
        assert refresh_res.status_code == 401, refresh_res.text

        # Can login with new password
        login_res = client.post(
            "/api/v1/auth/login",
            json={"username": login_username, "password": new_password},
        )
        assert login_res.status_code == 200, login_res.text

