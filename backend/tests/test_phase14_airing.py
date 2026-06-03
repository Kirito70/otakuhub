"""Phase 3.1 integration tests: airing calendar endpoint.

Tests the GET /api/v1/media/airing endpoint which returns upcoming episodes
with joined media metadata.
"""

from __future__ import annotations

from datetime import datetime, timedelta

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
        # If this fails, it means pytest_sessionstart didn't seed the admin
        assert login_resp.status_code == 200, (
            f"Admin login failed: {login_resp.status_code} {login_resp.text}. "
            "Is conftest.pytest_sessionstart running?"
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


async def _seed_episode(
    db: AsyncSession,
    media_id,
    episode_number: int = 1,
    *,
    title: str = "Test Episode",
    air_date: datetime | None = None,
    duration: int = 24,
) -> Episode:
    """Helper to create a single episode for testing."""
    if air_date is None:
        air_date = datetime.utcnow() + timedelta(days=1)
    episode = Episode(
        media_id=media_id,
        episode_number=episode_number,
        title=title,
        air_date=air_date,
        duration_minutes=duration,
    )
    db.add(episode)
    await db.commit()
    await db.refresh(episode)
    return episode


# =========================================================================
# Empty state
# =========================================================================


@pytest.mark.asyncio
async def test_airing_empty_state(auth_client: AsyncClient):
    """No episodes in DB should return empty items."""
    resp = await auth_client.get("/api/v1/media/airing")
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
async def test_airing_returns_episodes_with_media_metadata(auth_client: AsyncClient, db_session: AsyncSession):
    """Airing episodes should include joined media metadata."""
    media = await _get_first_media(db_session)
    episode = await _seed_episode(db_session, media.id)

    resp = await auth_client.get("/api/v1/media/airing")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["total"] >= 1
    assert body["offset"] == 0

    items = body["items"]
    # Find our seeded episode
    matches = [i for i in items if i["id"] == str(episode.id)]
    assert len(matches) == 1, f"Seeded episode not found in response: {items}"

    item = matches[0]
    assert item["media_id"] == str(media.id)
    assert item["media_title"] == media.title_romaji
    assert item["media_type"] == media.media_type
    assert item["episode_number"] == episode.episode_number
    assert item["title"] == episode.title
    assert item["duration_minutes"] == episode.duration_minutes


# =========================================================================
# Filter by media_type
# =========================================================================


@pytest.mark.asyncio
async def test_airing_filters_by_media_type(auth_client: AsyncClient, db_session: AsyncSession):
    """media_type parameter should filter results."""
    result = await db_session.exec(select(MediaEntry).limit(2))
    all_media = result.all()
    assert len(all_media) >= 1

    media = all_media[0]
    # Use a unique episode number to avoid any collision with previous tests
    await _seed_episode(db_session, media.id, episode_number=1001)

    # First: no filter should include our episode
    resp_all = await auth_client.get("/api/v1/media/airing")
    assert resp_all.status_code == 200, resp_all.text
    all_total = resp_all.json()["total"]
    assert all_total >= 1, "No episodes found without filter"

    # Filter by the media's type — should include at least our episode
    # Use .value to get the string value for the URL
    resp = await auth_client.get(f"/api/v1/media/airing?media_type={media.media_type.value}")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["total"] >= 1, (
        f"Expected >=1 episode with media_type={media.media_type.value}, got {body['total']}, "
        f"unfiltered total was {all_total}"
    )


# =========================================================================
# Date range filtering
# =========================================================================


@pytest.mark.asyncio
async def test_airing_date_range_limits_results(auth_client: AsyncClient, db_session: AsyncSession):
    """start_date and end_date should filter episodes by air_date."""
    media = await _get_first_media(db_session)

    # Create an episode airing far in the future
    far_future = datetime.utcnow() + timedelta(days=365)
    await _seed_episode(db_session, media.id, episode_number=10, air_date=far_future)

    # Query with a window that excludes the far-future episode
    near_future = (datetime.utcnow() + timedelta(days=30)).isoformat()
    resp = await auth_client.get(f"/api/v1/media/airing?end_date={near_future}")
    assert resp.status_code == 200, resp.text
    body = resp.json()

    # The far-future episode should NOT be in results
    far_future_ids = [
        i["id"] for i in body["items"]
        if i.get("episode_number") == 10
    ]
    assert len(far_future_ids) == 0, "Far-future episode should be excluded by end_date"

    # Query with a window that includes the far-future episode
    later = (datetime.utcnow() + timedelta(days=400)).isoformat()
    resp = await auth_client.get(
        f"/api/v1/media/airing?start_date={far_future.isoformat()}&end_date={later}"
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()

    far_future_included = [
        i for i in body["items"]
        if i.get("episode_number") == 10
    ]
    assert len(far_future_included) >= 1, (
        "Far-future episode should be included with wide date range"
    )


# =========================================================================
# Pagination
# =========================================================================


@pytest.mark.asyncio
async def test_airing_pagination(auth_client: AsyncClient, db_session: AsyncSession):
    """limit and offset should paginate results."""
    media = await _get_first_media(db_session)

    # Seed 3 episodes
    for i in range(1, 4):
        await _seed_episode(db_session, media.id, episode_number=i)

    # Request limit=1, offset=0
    resp = await auth_client.get("/api/v1/media/airing?limit=1&offset=0")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert len(body["items"]) == 1
    assert body["total"] >= 3

    # Request limit=1, offset=1 — should get a different episode
    resp2 = await auth_client.get("/api/v1/media/airing?limit=1&offset=1")
    assert resp2.status_code == 200, resp2.text
    body2 = resp2.json()
    assert len(body2["items"]) == 1
    assert body2["items"][0]["id"] != body["items"][0]["id"], (
        "Offset should return different items"
    )


# =========================================================================
# Auth required
# =========================================================================


@pytest.mark.asyncio
async def test_airing_requires_auth():
    """Unauthenticated requests should be rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/media/airing")
        assert resp.status_code == 401, resp.text


# =========================================================================
# Invalid parameters
# =========================================================================


@pytest.mark.asyncio
async def test_airing_rejects_invalid_limit(auth_client: AsyncClient):
    """limit out of range should return 422."""
    resp = await auth_client.get("/api/v1/media/airing?limit=0")
    assert resp.status_code == 422, resp.text

    resp = await auth_client.get("/api/v1/media/airing?limit=101")
    assert resp.status_code == 422, resp.text


@pytest.mark.asyncio
async def test_airing_rejects_negative_offset(auth_client: AsyncClient):
    """negative offset should return 422."""
    resp = await auth_client.get("/api/v1/media/airing?limit=-1")
    assert resp.status_code == 422, resp.text


# =========================================================================
# Past episodes (default window)
# =========================================================================


@pytest.mark.asyncio
async def test_airing_default_window_excludes_past(auth_client: AsyncClient, db_session: AsyncSession):
    """Default window should start from now, excluding past episodes."""
    media = await _get_first_media(db_session)

    # Create an episode with air_date in the past
    past_date = datetime.utcnow() - timedelta(days=7)
    await _seed_episode(
        db_session, media.id, episode_number=99,
        title="Past Episode", air_date=past_date,
    )

    # Default query (no start_date) should exclude past episodes
    resp = await auth_client.get("/api/v1/media/airing")
    assert resp.status_code == 200, resp.text
    body = resp.json()

    past_ids = [i for i in body["items"] if i.get("title") == "Past Episode"]
    assert len(past_ids) == 0, "Past episodes should be excluded by default window"
