"""Phase 25.3 integration tests: media source mappings endpoint.

Tests GET /api/v1/media/{media_id}/sources which returns available provider
source mappings with their episode lists.
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
from src.app.models import MediaEntry, MediaSourceMapping, MediaSourceEpisode


async def _create_test_media(db: AsyncSession) -> MediaEntry:
    """Create a dedicated test media entry to avoid state leakage."""
    from datetime import datetime, timezone
    import uuid

    media = MediaEntry(
        id=uuid.uuid4(),
        title_romaji=f"Test Media {uuid.uuid4().hex[:8]}",
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

ADMIN_USERNAME = "test_root_admin"
ADMIN_PASSWORD = "TestRoot123!"


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
async def db_session():
    """Provide a real async database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def _get_first_media(db: AsyncSession) -> MediaEntry:
    """Return the first media entry seeded by pytest_sessionstart."""
    result = await db.exec(select(MediaEntry).limit(1))
    media = result.one()
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
        match_confidence=Decimal("100.00"),
        is_streaming_enabled=True,
        has_sub=has_sub,
        has_dub=has_dub,
        episode_count=episode_count,
    )
    db.add(mapping)
    await db.commit()
    await db.refresh(mapping)
    return mapping


async def _seed_source_episode(
    db: AsyncSession,
    mapping_id,
    media_id,
    *,
    episode_number: float = 1.0,
    language: str = "sub",
    embed_url: str | None = "https://megaplay.buzz/embed/test",
    is_available: bool = True,
) -> MediaSourceEpisode:
    """Helper to create a source episode for testing."""
    unique_id = uuid4().hex[:8]
    ep = MediaSourceEpisode(
        mapping_id=mapping_id,
        media_id=media_id,
        source="anikoto",
        source_episode_id=f"ep-{unique_id}-{episode_number}-{language}",
        episode_number=Decimal(str(episode_number)),
        language=language,
        embed_url=embed_url,
        is_available=is_available,
    )
    db.add(ep)
    await db.commit()
    await db.refresh(ep)
    return ep


# =========================================================================
# Auth required
# =========================================================================


@pytest.mark.asyncio
async def test_sources_requires_auth():
    """Unauthenticated requests should be rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get(f"/api/v1/media/{uuid4()}/sources")
        assert resp.status_code == 401, resp.text


# =========================================================================
# Empty state
# =========================================================================


@pytest.mark.asyncio
async def test_sources_empty_state(auth_client: AsyncClient, db_session: AsyncSession):
    """Media with no source mappings should return empty items."""
    media = await _create_test_media(db_session)

    resp = await auth_client.get(f"/api/v1/media/{media.id}/sources")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0


# =========================================================================
# Success state — sources exist
# =========================================================================


@pytest.mark.asyncio
async def test_sources_returns_mappings(auth_client: AsyncClient, db_session: AsyncSession):
    """Source mappings should be returned with correct fields."""
    media = await _get_first_media(db_session)
    mapping = await _seed_mapping(db_session, media.id, episode_count=12)

    resp = await auth_client.get(f"/api/v1/media/{media.id}/sources")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["total"] >= 1

    matches = [m for m in body["items"] if m["id"] == str(mapping.id)]
    assert len(matches) == 1

    item = matches[0]
    assert item["source"] == "anikoto"
    assert item["source_title"] == "Naruto"
    assert item["mapping_status"] == "matched"
    assert item["is_streaming_enabled"] is True
    assert item["has_sub"] is True
    assert item["has_dub"] is False
    assert item["episode_count"] == 12
    assert item["episode_list"] == []


@pytest.mark.asyncio
async def test_sources_returns_episodes_in_mapping(
    auth_client: AsyncClient, db_session: AsyncSession,
):
    """Source mapping should include its episode list."""
    media = await _get_first_media(db_session)
    mapping = await _seed_mapping(db_session, media.id)
    source_ep = await _seed_source_episode(
        db_session, mapping.id, media.id,
        episode_number=1.0, language="sub",
    )

    resp = await auth_client.get(f"/api/v1/media/{media.id}/sources")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    matches = [m for m in body["items"] if m["id"] == str(mapping.id)]
    assert len(matches) == 1

    ep_list = matches[0]["episode_list"]
    assert len(ep_list) == 1
    ep = ep_list[0]
    assert ep["id"] == str(source_ep.id)
    assert ep["episode_number"] == 1.0
    assert ep["language"] == "sub"
    assert ep["embed_url"] == "https://megaplay.buzz/embed/test"
    assert ep["is_available"] is True


@pytest.mark.asyncio
async def test_sources_returns_multiple_sources(
    auth_client: AsyncClient, db_session: AsyncSession,
):
    """Media with multiple provider sources should return all of them."""
    media = await _get_first_media(db_session)
    await _seed_mapping(db_session, media.id, source="anikoto", source_media_id="ani-1", source_title="AniSrc")
    await _seed_mapping(db_session, media.id, source="megaplay", source_media_id="mega-1", source_title="MegaSrc")

    resp = await auth_client.get(f"/api/v1/media/{media.id}/sources")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["total"] >= 2

    sources = {m["source"] for m in body["items"]}
    assert "anikoto" in sources
    assert "megaplay" in sources


# =========================================================================
# Non-existent media
# =========================================================================


@pytest.mark.asyncio
async def test_sources_non_existent_media(auth_client: AsyncClient):
    """Non-existent media_id should return 200 with empty items."""
    fake_id = uuid4()
    resp = await auth_client.get(f"/api/v1/media/{fake_id}/sources")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0
