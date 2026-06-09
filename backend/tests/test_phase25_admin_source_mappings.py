"""Phase 25.7 integration tests: admin source-mapping management.

Tests GET /api/v1/admin/source-mappings (list with filters, pagination) and
PATCH /api/v1/admin/source-mappings/{id} (update mapping fields).
"""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.main import app
from src.app.database import AsyncSessionLocal
from src.app.models import MediaEntry, MediaSourceMapping

ADMIN_USERNAME = "test_root_admin"
ADMIN_PASSWORD = "TestRoot123!"


async def _create_test_media(db: AsyncSession) -> MediaEntry:
    """Create a dedicated test media entry to avoid state leakage."""
    from datetime import datetime, timezone

    media = MediaEntry(
        id=uuid4(),
        title_romaji=f"Test Media {uuid4().hex[:8]}",
        media_type="anime",
        format="TV",
        status="releasing",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media


async def _seed_mapping(
    db: AsyncSession,
    media_id,
    *,
    source: str = "anikoto",
    source_media_id: str | None = None,
    source_title: str = "Naruto",
    mapping_status: str = "matched",
    has_sub: bool = True,
    has_dub: bool = False,
    episode_count: int | None = None,
    match_confidence: Decimal | None = None,
) -> MediaSourceMapping:
    """Helper to create a source mapping for testing."""
    if source_media_id is None:
        source_media_id = f"{source}-{uuid4().hex[:8]}"
    mapping = MediaSourceMapping(
        media_id=media_id,
        source=source,
        source_media_id=source_media_id,
        source_title=source_title,
        mapping_status=mapping_status,
        match_confidence=match_confidence or Decimal("100.00"),
        is_streaming_enabled=True,
        has_sub=has_sub,
        has_dub=has_dub,
        episode_count=episode_count,
    )
    db.add(mapping)
    await db.commit()
    await db.refresh(mapping)
    return mapping


@pytest.fixture
async def auth_client():
    """Return an AsyncClient with admin auth already logged in."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        login_resp = await ac.post("/api/v1/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD,
        })
        assert login_resp.status_code == 200, (
            f"Admin login failed: {login_resp.status_code} {login_resp.text}"
        )
        token = login_resp.json()["access_token"]
        ac.headers["Authorization"] = f"Bearer {token}"
        yield ac


@pytest.fixture
async def unauth_client():
    """Return an AsyncClient without auth headers (no token)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
async def normal_user_client():
    """Return an AsyncClient logged in as a non-admin user.

    Public registration is locked after bootstrap, so we create the user
    via the admin user-management endpoint.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        # First login as admin
        admin_resp = await ac.post("/api/v1/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD,
        })
        assert admin_resp.status_code == 200, f"Admin login failed: {admin_resp.text}"
        admin_token = admin_resp.json()["access_token"]

        # Create a normal user via admin endpoint
        username = f"normal_{uuid4().hex[:8]}"
        create_resp = await ac.post("/api/v1/users", json={
            "username": username,
            "email": f"{username}@test.local",
            "password": "NormalUser123!",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert create_resp.status_code == 201, f"User creation failed: {create_resp.text}"

        # Login as the new normal user
        login_resp = await ac.post("/api/v1/auth/login", json={
            "username": username,
            "password": "NormalUser123!",
        })
        assert login_resp.status_code == 200, f"Normal user login failed: {login_resp.text}"
        token = login_resp.json()["access_token"]
        ac.headers["Authorization"] = f"Bearer {token}"
        yield ac


@pytest.fixture
async def db_session():
    """Provide a real async database session."""
    async with AsyncSessionLocal() as session:
        yield session


# ── GET /admin/source-mappings ─────────────────────────────────────────────


async def _delete_all_mappings(db: AsyncSession) -> None:
    """Remove all source mappings for test isolation."""
    result = await db.exec(select(MediaSourceMapping))
    for m in result.all():
        await db.delete(m)
    await db.commit()


class TestAdminListSourceMappings:
    ENDPOINT = "/api/v1/admin/source-mappings"

    @pytest.fixture(autouse=True)
    async def _cleanup(self, db_session: AsyncSession) -> None:
        """Remove all mappings before each test for isolation."""
        await _delete_all_mappings(db_session)

    async def test_requires_auth(self, unauth_client: AsyncClient) -> None:
        """401 when no auth token is provided."""
        resp = await unauth_client.get(self.ENDPOINT)
        assert resp.status_code == 401

    async def test_requires_admin(self, normal_user_client: AsyncClient) -> None:
        """403 when a non-admin user tries to access."""
        resp = await normal_user_client.get(self.ENDPOINT)
        assert resp.status_code == 403

    async def test_empty_list(self, auth_client: AsyncClient) -> None:
        """Returns empty list when no mappings exist."""
        resp = await auth_client.get(self.ENDPOINT)
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["limit"] == 50
        assert data["offset"] == 0

    async def test_returns_all_mappings_paginated(
        self, auth_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Returns mappings with pagination."""
        media = await _create_test_media(db_session)
        m1 = await _seed_mapping(db_session, media.id, source="anikoto", source_title="Title A")
        m2 = await _seed_mapping(db_session, media.id, source="megaplay", source_title="Title B")
        m3 = await _seed_mapping(db_session, media.id, source="anikoto", source_title="Title C")

        # Fetch all
        resp = await auth_client.get(self.ENDPOINT)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

        # Fetch with limit=2
        resp = await auth_client.get(f"{self.ENDPOINT}?limit=2")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2
        assert data["limit"] == 2

    async def test_filters_by_source(
        self, auth_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Filters mappings by source name."""
        media = await _create_test_media(db_session)
        await _seed_mapping(db_session, media.id, source="anikoto", source_title="Anime A")
        await _seed_mapping(db_session, media.id, source="megaplay", source_title="Manga B")

        resp = await auth_client.get(f"{self.ENDPOINT}?source=anikoto")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["source"] == "anikoto"

    async def test_filters_by_mapping_status(
        self, auth_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Filters mappings by mapping status."""
        media = await _create_test_media(db_session)
        await _seed_mapping(db_session, media.id, source="anikoto", mapping_status="matched", source_title="Matched")
        await _seed_mapping(db_session, media.id, source="megaplay", mapping_status="unmatched", source_title="Unmatched")
        await _seed_mapping(db_session, media.id, source="other", mapping_status="stale", source_title="Stale")

        resp = await auth_client.get(f"{self.ENDPOINT}?mapping_status=unmatched")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["mapping_status"] == "unmatched"

    async def test_returns_full_item_fields(
        self, auth_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Each returned item has all expected fields."""
        media = await _create_test_media(db_session)
        mapping = await _seed_mapping(
            db_session, media.id,
            source="anikoto",
            source_media_id="test-series-1",
            source_title="Test Anime",
            mapping_status="matched",
            has_sub=True,
            has_dub=True,
            episode_count=24,
        )

        resp = await auth_client.get(self.ENDPOINT)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        item = data["items"][0]
        assert item["id"] == str(mapping.id)
        assert item["media_id"] == str(media.id)
        assert item["source"] == "anikoto"
        assert item["source_media_id"] == "test-series-1"
        assert item["source_title"] == "Test Anime"
        assert item["mapping_status"] == "matched"
        assert item["is_streaming_enabled"] is True
        assert item["has_sub"] is True
        assert item["has_dub"] is True
        assert item["episode_count"] == 24
        assert item["first_seen_at"] is not None
        assert item["last_seen_at"] is not None
        assert item["created_at"] is not None
        assert item["updated_at"] is not None


# ── PATCH /admin/source-mappings/{id} ──────────────────────────────────────


class TestAdminUpdateSourceMapping:
    ENDPOINT = "/api/v1/admin/source-mappings"

    @pytest.fixture(autouse=True)
    async def _cleanup(self, db_session: AsyncSession) -> None:
        """Remove all mappings before each test for isolation."""
        await _delete_all_mappings(db_session)

    async def _create_test_mapping(self, db_session: AsyncSession) -> tuple[MediaEntry, MediaSourceMapping]:
        """Create a media + mapping for PATCH tests."""
        media = await _create_test_media(db_session)
        mapping = await _seed_mapping(
            db_session, media.id,
            source="anikoto",
            source_title="Original Title",
            mapping_status="matched",
            match_confidence=Decimal("100.00"),
            has_sub=True,
            has_dub=False,
            episode_count=12,
        )
        return media, mapping

    async def test_requires_auth(self, unauth_client: AsyncClient, db_session: AsyncSession) -> None:
        """401 when no auth token is provided."""
        _, mapping = await self._create_test_mapping(db_session)
        resp = await unauth_client.patch(f"{self.ENDPOINT}/{mapping.id}", json={"mapping_status": "stale"})
        assert resp.status_code == 401

    async def test_requires_admin(self, normal_user_client: AsyncClient, db_session: AsyncSession) -> None:
        """403 when a non-admin user tries to access."""
        _, mapping = await self._create_test_mapping(db_session)
        resp = await normal_user_client.patch(f"{self.ENDPOINT}/{mapping.id}", json={"mapping_status": "stale"})
        assert resp.status_code == 403

    async def test_404_for_nonexistent_mapping(self, auth_client: AsyncClient) -> None:
        """404 when mapping ID does not exist."""
        fake_id = uuid4()
        resp = await auth_client.patch(f"{self.ENDPOINT}/{fake_id}", json={"mapping_status": "stale"})
        assert resp.status_code == 404

    async def test_update_mapping_status(
        self, auth_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """PATCH updates mapping_status."""
        _, mapping = await self._create_test_mapping(db_session)
        resp = await auth_client.patch(
            f"{self.ENDPOINT}/{mapping.id}",
            json={"mapping_status": "stale"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["mapping_status"] == "stale"

    async def test_update_match_confidence(
        self, auth_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """PATCH updates match_confidence."""
        _, mapping = await self._create_test_mapping(db_session)
        resp = await auth_client.patch(
            f"{self.ENDPOINT}/{mapping.id}",
            json={"match_confidence": 85.5},
        )
        assert resp.status_code == 200
        data = resp.json()
        # Decimal serializes to string in JSON
        assert float(data["match_confidence"]) == 85.5

    async def test_update_streaming_flags(
        self, auth_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """PATCH updates streaming boolean flags."""
        _, mapping = await self._create_test_mapping(db_session)
        resp = await auth_client.patch(
            f"{self.ENDPOINT}/{mapping.id}",
            json={"is_streaming_enabled": False, "has_dub": True},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_streaming_enabled"] is False
        assert data["has_dub"] is True

    async def test_update_episode_count(
        self, auth_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """PATCH updates episode_count."""
        _, mapping = await self._create_test_mapping(db_session)
        resp = await auth_client.patch(
            f"{self.ENDPOINT}/{mapping.id}",
            json={"episode_count": 26},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["episode_count"] == 26

    async def test_update_source_title(
        self, auth_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """PATCH updates source_title."""
        _, mapping = await self._create_test_mapping(db_session)
        resp = await auth_client.patch(
            f"{self.ENDPOINT}/{mapping.id}",
            json={"source_title": "Renamed Title"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["source_title"] == "Renamed Title"

    async def test_partial_update_only_changes_sent_fields(
        self, auth_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Only fields in the PATCH body are changed; others preserved."""
        _, mapping = await self._create_test_mapping(db_session)
        resp = await auth_client.patch(
            f"{self.ENDPOINT}/{mapping.id}",
            json={"source_title": "Only Title Changed"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["source_title"] == "Only Title Changed"
        # Other fields preserved
        assert data["mapping_status"] == "matched"
        assert data["has_sub"] is True
        assert data["episode_count"] == 12

    async def test_empty_body_returns_400(
        self, auth_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """400 when no fields are provided in the PATCH body."""
        _, mapping = await self._create_test_mapping(db_session)
        resp = await auth_client.patch(
            f"{self.ENDPOINT}/{mapping.id}",
            json={},
        )
        assert resp.status_code == 400
        assert "No fields to update" in resp.text

    async def test_invalid_mapping_status_returns_422(
        self, auth_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """422 when mapping_status is not a valid value."""
        _, mapping = await self._create_test_mapping(db_session)
        resp = await auth_client.patch(
            f"{self.ENDPOINT}/{mapping.id}",
            json={"mapping_status": "invalid_status_xyz"},
        )
        assert resp.status_code == 422
        assert "Invalid mapping_status" in resp.text
