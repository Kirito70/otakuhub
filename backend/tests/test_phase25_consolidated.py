"""Phase 25.4 integration tests: consolidated episodes/sources endpoint.

Tests GET /api/v1/media/{media_id}/episodes/sources which merges canonical
episodes with provider source data deduplicated by episode number.
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
from src.app.models import MediaEntry, Episode, MediaSourceMapping, MediaSourceEpisode

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


async def _seed_canon_episode(
    db: AsyncSession,
    media_id,
    episode_number: int = 1,
    *,
    title: str = "Canon Ep",
) -> Episode:
    """Helper to create a canonical episode."""
    ep = Episode(media_id=media_id, episode_number=episode_number, title=title)
    db.add(ep)
    await db.commit()
    await db.refresh(ep)
    return ep


async def _seed_mapping(
    db: AsyncSession,
    media_id,
    *,
    source: str = "anikoto",
) -> MediaSourceMapping:
    """Helper to create a source mapping."""
    mapping = MediaSourceMapping(
        media_id=media_id,
        source=source,
        source_media_id=f"{source}-{uuid4().hex[:8]}",
        source_title="Test Source",
        mapping_status="matched",
        match_confidence=Decimal("100.00"),
        is_streaming_enabled=True,
        has_sub=True,
        has_dub=False,
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
    source: str = "anikoto",
    language: str = "sub",
    embed_url: str | None = "https://megaplay.buzz/embed/test",
) -> MediaSourceEpisode:
    """Helper to create a source episode."""
    ep = MediaSourceEpisode(
        mapping_id=mapping_id,
        media_id=media_id,
        source=source,
        source_episode_id=f"{uuid4().hex[:8]}-ep-{episode_number}",
        episode_number=Decimal(str(episode_number)),
        language=language,
        embed_url=embed_url,
        is_available=True,
    )
    db.add(ep)
    await db.commit()
    await db.refresh(ep)
    return ep


# =========================================================================
# Auth required
# =========================================================================


@pytest.mark.asyncio
async def test_consolidated_requires_auth():
    """Unauthenticated requests should be rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get(f"/api/v1/media/{uuid4()}/episodes/sources")
        assert resp.status_code == 401, resp.text


# =========================================================================
# Empty state
# =========================================================================


@pytest.mark.asyncio
async def test_consolidated_empty_state(auth_client: AsyncClient, db_session: AsyncSession):
    """Media with no episodes should return empty items."""
    media = await _create_test_media(db_session)

    resp = await auth_client.get(f"/api/v1/media/{media.id}/episodes/sources")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0


# =========================================================================
# Canonical-only (no source episodes)
# =========================================================================


@pytest.mark.asyncio
async def test_consolidated_canonical_only(auth_client: AsyncClient, db_session: AsyncSession):
    """With canonical episodes but no source data, episodes appear with empty sources."""
    media = await _create_test_media(db_session)
    await _seed_canon_episode(db_session, media.id, episode_number=1, title="No Source Ep")

    resp = await auth_client.get(f"/api/v1/media/{media.id}/episodes/sources")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["total"] >= 1

    items = body["items"]
    match = [i for i in items if i.get("canonical_title") == "No Source Ep"]
    assert len(match) == 1

    item = match[0]
    assert item["episode_number"] == 1.0
    assert item["canonical_title"] == "No Source Ep"
    assert item["sources"] == []


# =========================================================================
# Canonical + source episodes merged
# =========================================================================


@pytest.mark.asyncio
async def test_consolidated_sources_attached(
    auth_client: AsyncClient, db_session: AsyncSession,
):
    """Canonical episodes should have source episodes attached by number."""
    media = await _create_test_media(db_session)
    await _seed_canon_episode(db_session, media.id, episode_number=5, title="Ep 5")

    mapping = await _seed_mapping(db_session, media.id)
    await _seed_source_episode(
        db_session, mapping.id, media.id,
        episode_number=5.0, language="sub",
        embed_url="https://megaplay.buzz/embed/ep5",
    )

    resp = await auth_client.get(f"/api/v1/media/{media.id}/episodes/sources")
    assert resp.status_code == 200, resp.text

    items = resp.json()["items"]
    match = [i for i in items if i.get("episode_number") == 5.0]
    assert len(match) >= 1

    item = match[0]
    assert item["canonical_title"] == "Ep 5"
    assert len(item["sources"]) == 1

    src = item["sources"][0]
    assert src["source"] == "anikoto"
    assert src["language"] == "sub"
    assert src["embed_url"] == "https://megaplay.buzz/embed/ep5"
    assert src["is_available"] is True


@pytest.mark.asyncio
async def test_consolidated_multiple_sources_per_episode(
    auth_client: AsyncClient, db_session: AsyncSession,
):
    """A single episode can have multiple source options (sub + dub, different providers)."""
    media = await _create_test_media(db_session)
    await _seed_canon_episode(db_session, media.id, episode_number=3, title="Ep 3")

    mapping = await _seed_mapping(db_session, media.id, source="anikoto")
    await _seed_source_episode(
        db_session, mapping.id, media.id,
        episode_number=3.0, language="sub",
        embed_url="https://megaplay.buzz/embed/sub",
    )
    await _seed_source_episode(
        db_session, mapping.id, media.id,
        episode_number=3.0, language="dub",
        embed_url="https://megaplay.buzz/embed/dub",
    )

    resp = await auth_client.get(f"/api/v1/media/{media.id}/episodes/sources")
    assert resp.status_code == 200, resp.text

    items = resp.json()["items"]
    match = [i for i in items if i.get("episode_number") == 3.0]
    assert len(match) >= 1

    sources = match[0]["sources"]
    assert len(sources) == 2

    languages = {s["language"] for s in sources}
    assert "sub" in languages
    assert "dub" in languages


# =========================================================================
# Pagination
# =========================================================================


@pytest.mark.asyncio
async def test_consolidated_pagination(auth_client: AsyncClient, db_session: AsyncSession):
    """limit and offset should paginate canonical episodes, sources not paginated.

    Uses a dedicated media entry to avoid ordering conflicts from shared
    test data seeded by earlier tests on the same media entry.
    """
    # Create a test-specific media entry (avoid state leakage from shared fixture)
    from datetime import datetime, timezone
    import uuid

    media = MediaEntry(
        id=uuid.uuid4(),
        title_romaji="Pagination Test Media",
        media_type="anime",
        format="TV",
        status="releasing",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(media)
    await db_session.commit()
    await db_session.refresh(media)

    # Seed 3 episodes
    for i in range(1, 4):
        await _seed_canon_episode(db_session, media.id, episode_number=i, title=f"Ep{i}")

    resp = await auth_client.get(f"/api/v1/media/{media.id}/episodes/sources?limit=2&offset=0")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert len(body["items"]) == 2
    assert body["total"] >= 3
    assert body["items"][0]["episode_number"] < body["items"][1]["episode_number"], (
        "Items should be ordered by episode_number ascending"
    )

    # Second page
    resp2 = await auth_client.get(f"/api/v1/media/{media.id}/episodes/sources?limit=2&offset=2")
    assert resp2.status_code == 200, resp2.text
    body2 = resp2.json()
    assert len(body2["items"]) >= 1
    assert body2["items"][0]["episode_number"] >= 3.0


# =========================================================================
# Invalid parameters
# =========================================================================


@pytest.mark.asyncio
async def test_consolidated_rejects_invalid_limit(auth_client: AsyncClient):
    """limit out of range should return 422."""
    media_id = uuid4()
    resp = await auth_client.get(f"/api/v1/media/{media_id}/episodes/sources?limit=0")
    assert resp.status_code == 422, resp.text

    resp = await auth_client.get(f"/api/v1/media/{media_id}/episodes/sources?limit=101")
    assert resp.status_code == 422, resp.text


# =========================================================================
# Non-existent media
# =========================================================================


@pytest.mark.asyncio
async def test_consolidated_non_existent_media(auth_client: AsyncClient):
    """Non-existent media_id should return 200 with empty items."""
    fake_id = uuid4()
    resp = await auth_client.get(f"/api/v1/media/{fake_id}/episodes/sources")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0
