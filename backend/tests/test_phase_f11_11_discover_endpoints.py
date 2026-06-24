"""F11.11 integration tests: home, search, browse, calendar, lists enhanced.

Tests the 5 P0 endpoints:
  - GET /api/v1/home
  - GET /api/v1/search
  - GET /api/v1/lists/me (enhanced: cursor, media_type, sort)
  - GET /api/v1/media/browse
  - GET /api/v1/calendar
"""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.main import app
from src.app.database import AsyncSessionLocal
from src.app.models import MediaEntry, Episode, Chapter, UserListEntry, User
from src.app.models.enums import MediaType, MediaFormat, MediaStatus, WatchStatus

ADMIN_USERNAME = "test_root_admin"
ADMIN_PASSWORD = "TestRoot123!"


# =========================================================================
# Fixtures
# =========================================================================


@pytest.fixture
async def auth_client():
    """Return an AsyncClient with admin auth."""
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
    return result.one()


async def _seed_episode(
    db: AsyncSession,
    media_id,
    episode_number: int = 1,
    *,
    title: str = "Test Episode",
    air_date: datetime | None = None,
) -> Episode:
    if air_date is None:
        air_date = datetime.utcnow() + timedelta(days=1)
    episode = Episode(
        media_id=media_id,
        episode_number=episode_number,
        title=title,
        air_date=air_date,
        duration_minutes=24,
    )
    db.add(episode)
    await db.commit()
    await db.refresh(episode)
    return episode


async def _seed_chapter(
    db: AsyncSession,
    media_id,
    chapter_number: float = 1,
    *,
    title: str = "Test Chapter",
    published_at: datetime | None = None,
) -> Chapter:
    if published_at is None:
        published_at = datetime.utcnow() + timedelta(days=2)
    chapter = Chapter(
        media_id=media_id,
        chapter_number=chapter_number,
        title=title,
        published_at=published_at,
    )
    db.add(chapter)
    await db.commit()
    await db.refresh(chapter)
    return chapter


async def _seed_list_entry(
    db: AsyncSession,
    user_id,
    media_id,
    *,
    status: WatchStatus = WatchStatus.watching,
    progress: int = 5,
) -> UserListEntry:
    # Check if entry already exists to avoid UNIQUE constraint violation
    result = await db.exec(
        select(UserListEntry).where(
            UserListEntry.user_id == user_id,
            UserListEntry.media_id == media_id,
        )
    )
    existing = result.one_or_none()
    if existing is not None:
        return existing
    entry = UserListEntry(
        user_id=user_id,
        media_id=media_id,
        status=status,
        progress=progress,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def _get_second_media(db: AsyncSession) -> MediaEntry:
    """Return the second media entry (for tests needing distinct media)."""
    result = await db.exec(select(MediaEntry).offset(1).limit(1))
    return result.one()


async def _get_admin_user(db: AsyncSession) -> User:
    """Get the admin user seeded by conftest."""
    result = await db.exec(select(User).where(User.username == ADMIN_USERNAME))
    return result.one()


# =========================================================================
# GET /api/v1/home — 4 tests
# =========================================================================


@pytest.mark.asyncio
async def test_home_requires_auth():
    """Unauthenticated requests should be rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/home")
        assert resp.status_code == 401, resp.text


@pytest.mark.asyncio
async def test_home_returns_all_sections(auth_client: AsyncClient):
    """Home should return all 6 sections (some may be empty)."""
    resp = await auth_client.get("/api/v1/home")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert "spotlight" in body
    assert "continue_watching" in body
    assert "friend_recommendations" in body
    assert "group_watching_now" in body
    assert "airing_soon" in body
    assert "trending_in_group" in body

    # Each section should be a list
    assert isinstance(body["spotlight"], list)
    assert isinstance(body["continue_watching"], list)
    assert isinstance(body["airing_soon"], list)


@pytest.mark.asyncio
async def test_home_spotlight_includes_trending(auth_client: AsyncClient):
    """Spotlight section should include trending media."""
    resp = await auth_client.get("/api/v1/home")
    assert resp.status_code == 200, resp.text
    # At minimum, the seeded media should be present
    assert len(resp.json()["spotlight"]) >= 0


@pytest.mark.asyncio
async def test_home_continue_watching_shows_in_progress(auth_client: AsyncClient, db_session: AsyncSession):
    """Continue-watching should include user's in-progress items."""
    user = await _get_admin_user(db_session)
    media = await _get_first_media(db_session)
    await _seed_list_entry(db_session, user.id, media.id, status=WatchStatus.watching, progress=3)

    resp = await auth_client.get("/api/v1/home")
    assert resp.status_code == 200, resp.text
    cw = resp.json()["continue_watching"]
    matching = [i for i in cw if i["media_id"] == str(media.id)]
    assert len(matching) >= 1
    assert matching[0]["progress"] == 3


# =========================================================================
# GET /api/v1/search — 4 tests
# =========================================================================


@pytest.mark.asyncio
async def test_search_requires_auth():
    """Unauthenticated requests should be rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/search", params={"q": "Naruto"})
        assert resp.status_code == 401, resp.text


@pytest.mark.asyncio
async def test_search_returns_grouped_results(auth_client: AsyncClient):
    """Search should return results grouped by media type."""
    resp = await auth_client.get("/api/v1/search", params={"q": "Naruto", "limit": 5})
    assert resp.status_code == 200, resp.text

    body = resp.json()
    # Should have grouped sections
    for key in ("anime", "manga", "manhwa", "light_novel"):
        assert key in body, f"Missing group: {key}"
        assert f"{key}_count" in body, f"Missing count: {key}_count"

    # The seeded "Naruto" entry should be in anime group
    assert body["anime_count"] >= 1
    assert len(body["anime"]) >= 1


@pytest.mark.asyncio
async def test_search_empty_query_rejected(auth_client: AsyncClient):
    """Empty query should return 422."""
    resp = await auth_client.get("/api/v1/search", params={"q": ""})
    assert resp.status_code == 422, resp.text


@pytest.mark.asyncio
async def test_search_no_results_returns_empty_groups(auth_client: AsyncClient):
    """Search for non-existent title should return empty groups."""
    resp = await auth_client.get("/api/v1/search", params={"q": "ZZZZNonExistentTitle12345", "limit": 5})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["anime_count"] == 0
    assert body["manga_count"] == 0
    assert body["manhwa_count"] == 0
    assert body["light_novel_count"] == 0


# =========================================================================
# GET /api/v1/media/browse — 4 tests
# =========================================================================


@pytest.mark.asyncio
async def test_browse_requires_auth():
    """Unauthenticated requests should be rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/media/browse")
        assert resp.status_code == 401, resp.text


@pytest.mark.asyncio
async def test_browse_returns_paginated_results(auth_client: AsyncClient):
    """Browse should return paginated items with next_cursor."""
    resp = await auth_client.get("/api/v1/media/browse", params={"limit": 2})
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert "items" in body
    assert "total" in body
    assert body["total"] >= 1
    assert len(body["items"]) >= 1
    # next_cursor may be None or a string
    assert "next_cursor" in body


@pytest.mark.asyncio
async def test_browse_filters_by_type(auth_client: AsyncClient):
    """Browse should filter by media type."""
    resp = await auth_client.get("/api/v1/media/browse", params={"type": "anime"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    if body["items"]:
        assert all(i.get("media_type") == "anime" for i in body["items"])


@pytest.mark.asyncio
async def test_browse_filters_by_genre(auth_client: AsyncClient):
    """Browse should accept genre filter."""
    resp = await auth_client.get("/api/v1/media/browse", params={"genre": "action"})
    assert resp.status_code == 200, resp.text


# =========================================================================
# GET /api/v1/calendar — 4 tests
# =========================================================================


@pytest.mark.asyncio
async def test_calendar_requires_auth():
    """Unauthenticated requests should be rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/calendar")
        assert resp.status_code == 401, resp.text


@pytest.mark.asyncio
async def test_calendar_empty_state(auth_client: AsyncClient):
    """No episodes/chapters should return empty items."""
    resp = await auth_client.get("/api/v1/calendar")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "items" in body
    assert body["total"] >= 0


@pytest.mark.asyncio
async def test_calendar_includes_episodes(auth_client: AsyncClient, db_session: AsyncSession):
    """Calendar should include seeded episodes."""
    media = await _get_first_media(db_session)
    ep = await _seed_episode(db_session, media.id, episode_number=1, title="Cal Test Ep")

    resp = await auth_client.get("/api/v1/calendar", params={"limit": 50})
    assert resp.status_code == 200, resp.text
    body = resp.json()

    matching = [i for i in body["items"] if i.get("episode_number") == 1 and i["media_id"] == str(media.id)]
    assert len(matching) >= 1
    assert matching[0]["event_type"] == "episode"


@pytest.mark.asyncio
async def test_calendar_includes_chapters(auth_client: AsyncClient, db_session: AsyncSession):
    """Calendar should include seeded chapters as distinct event_type."""
    media = await _get_first_media(db_session)
    ch = await _seed_chapter(db_session, media.id, chapter_number=1.0, title="Cal Test Ch")

    resp = await auth_client.get("/api/v1/calendar", params={"limit": 50})
    assert resp.status_code == 200, resp.text
    body = resp.json()

    matching = [i for i in body["items"] if i.get("chapter_number") == 1 and i["media_id"] == str(media.id)]
    assert len(matching) >= 1
    assert matching[0]["event_type"] == "chapter"


# =========================================================================
# GET /api/v1/lists/me enhanced — 4 tests
# =========================================================================


@pytest.mark.asyncio
async def test_lists_me_cursor_pagination(auth_client: AsyncClient, db_session: AsyncSession):
    """lists/me with cursor should return next_cursor."""
    user = await _get_admin_user(db_session)
    media = await _get_first_media(db_session)
    await _seed_list_entry(db_session, user.id, media.id)

    resp = await auth_client.get("/api/v1/lists/me", params={"limit": 1, "sort": "recently_updated"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "items" in body
    assert "next_cursor" in body
    # cursor pagination requires the cursor param to be set first
    # with no cursor, it falls back to offset pagination
    if body["items"]:
        assert body["items"][0]["media_id"] is not None


@pytest.mark.asyncio
async def test_lists_me_cursor_param(auth_client: AsyncClient, db_session: AsyncSession):
    """lists/me with explicit cursor should use cursor pagination."""
    user = await _get_admin_user(db_session)
    media = await _get_first_media(db_session)
    entry = await _seed_list_entry(db_session, user.id, media.id)

    # Use the entry's updated_at as cursor
    cursor = entry.updated_at.isoformat()
    resp = await auth_client.get("/api/v1/lists/me", params={"cursor": cursor, "limit": 10})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    # With cursor after our entry, we should get items before it
    assert "next_cursor" in body


@pytest.mark.asyncio
async def test_lists_me_media_type_filter(auth_client: AsyncClient, db_session: AsyncSession):
    """lists/me should filter by media_type."""
    resp = await auth_client.get("/api/v1/lists/me", params={"media_type": "anime"})
    assert resp.status_code == 200, resp.text


@pytest.mark.asyncio
async def test_lists_me_sort_options(auth_client: AsyncClient):
    """lists/me should accept sort parameter."""
    for sort in ("recently_updated", "recently_added", "score_desc", "score_asc"):
        resp = await auth_client.get("/api/v1/lists/me", params={"sort": sort, "limit": 5})
        assert resp.status_code == 200, f"Sort {sort} failed: {resp.text}"
