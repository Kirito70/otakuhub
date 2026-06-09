"""Phase 25.1 integration tests: canonical episode list endpoint.

Tests GET /api/v1/media/{media_id}/episodes which returns the canonical
episode list ordered by episode number.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.main import app
from src.app.database import AsyncSessionLocal
from src.app.models import MediaEntry, Episode

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


async def _seed_episode(
    db: AsyncSession,
    media_id,
    episode_number: int = 1,
    *,
    title: str | None = None,
    air_date=None,
) -> Episode:
    """Helper to create a single episode for testing."""
    episode = Episode(
        media_id=media_id,
        episode_number=episode_number,
        title=title,
    )
    db.add(episode)
    await db.commit()
    await db.refresh(episode)
    return episode


# =========================================================================
# Auth required
# =========================================================================


@pytest.mark.asyncio
async def test_episodes_requires_auth():
    """Unauthenticated requests should be rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get(f"/api/v1/media/{uuid4()}/episodes")
        assert resp.status_code == 401, resp.text


# =========================================================================
# Empty state
# =========================================================================


@pytest.mark.asyncio
async def test_episodes_empty_state(auth_client: AsyncClient, db_session: AsyncSession):
    """Media with no episodes should return empty items."""
    media = await _create_test_media(db_session)

    resp = await auth_client.get(f"/api/v1/media/{media.id}/episodes")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["limit"] == 20
    assert body["offset"] == 0


# =========================================================================
# Success state — episodes exist
# =========================================================================


@pytest.mark.asyncio
async def test_episodes_returns_episodes_ordered_by_number(
    auth_client: AsyncClient, db_session: AsyncSession,
):
    """Episodes should be returned in ascending order by episode_number."""
    media = await _get_first_media(db_session)

    # Seed 3 episodes in non-sequential order
    await _seed_episode(db_session, media.id, episode_number=3, title="E3")
    await _seed_episode(db_session, media.id, episode_number=1, title="E1")
    await _seed_episode(db_session, media.id, episode_number=2, title="E2")

    resp = await auth_client.get(f"/api/v1/media/{media.id}/episodes")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["total"] >= 3

    items = body["items"]
    # Filter to our seeded episodes
    ours = [i for i in items if i["title"] in ("E1", "E2", "E3")]
    assert len(ours) == 3

    # Verify ordering
    numbers = [i["episode_number"] for i in ours]
    assert numbers == sorted(numbers), f"Episodes not in ascending order: {numbers}"


@pytest.mark.asyncio
async def test_episodes_returns_correct_fields(
    auth_client: AsyncClient, db_session: AsyncSession,
):
    """Each episode item should include the expected fields."""
    media = await _get_first_media(db_session)
    episode = await _seed_episode(db_session, media.id, episode_number=1, title="Correct Fields")

    resp = await auth_client.get(f"/api/v1/media/{media.id}/episodes")
    assert resp.status_code == 200, resp.text

    items = resp.json()["items"]
    match = [i for i in items if i["id"] == str(episode.id)]
    assert len(match) == 1

    item = match[0]
    assert item["episode_number"] == 1
    assert item["title"] == "Correct Fields"
    assert "air_date" in item
    assert "duration_minutes" in item
    assert "thumbnail_url" in item


# =========================================================================
# Pagination
# =========================================================================


@pytest.mark.asyncio
async def test_episodes_pagination(auth_client: AsyncClient, db_session: AsyncSession):
    """limit and offset should paginate results."""
    media = await _get_first_media(db_session)

    # Seed 3 episodes
    for i in range(1, 4):
        await _seed_episode(db_session, media.id, episode_number=i, title=f"E{i}")

    # Request limit=1, offset=0
    resp = await auth_client.get(f"/api/v1/media/{media.id}/episodes?limit=1&offset=0")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert len(body["items"]) == 1
    assert body["total"] >= 3

    # Request limit=1, offset=1 — should get a different episode
    resp2 = await auth_client.get(f"/api/v1/media/{media.id}/episodes?limit=1&offset=1")
    assert resp2.status_code == 200, resp2.text
    body2 = resp2.json()
    assert len(body2["items"]) == 1
    assert body2["items"][0]["id"] != body["items"][0]["id"], (
        "Offset should return different items"
    )


# =========================================================================
# Invalid parameters
# =========================================================================


@pytest.mark.asyncio
async def test_episodes_rejects_invalid_limit(auth_client: AsyncClient):
    """limit out of range should return 422."""
    media_id = uuid4()
    resp = await auth_client.get(f"/api/v1/media/{media_id}/episodes?limit=0")
    assert resp.status_code == 422, resp.text

    resp = await auth_client.get(f"/api/v1/media/{media_id}/episodes?limit=101")
    assert resp.status_code == 422, resp.text


@pytest.mark.asyncio
async def test_episodes_rejects_negative_offset(auth_client: AsyncClient):
    """negative offset should return 422."""
    media_id = uuid4()
    resp = await auth_client.get(f"/api/v1/media/{media_id}/episodes?limit=-1")
    assert resp.status_code == 422, resp.text


# =========================================================================
# Non-existent media
# =========================================================================


@pytest.mark.asyncio
async def test_episodes_non_existent_media(auth_client: AsyncClient):
    """Non-existent media_id should return 200 with empty items, not 404."""
    fake_id = uuid4()
    resp = await auth_client.get(f"/api/v1/media/{fake_id}/episodes")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0
