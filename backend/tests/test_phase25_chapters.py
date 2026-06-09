"""Phase 25.2 integration tests: canonical chapter list endpoint.

Tests GET /api/v1/media/{media_id}/chapters which returns the canonical
chapter list ordered by chapter number.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.main import app
from src.app.database import AsyncSessionLocal
from src.app.models import MediaEntry, Chapter


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


async def _seed_chapter(
    db: AsyncSession,
    media_id,
    chapter_number: float = 1.0,
    *,
    title: str = "Test Chapter",
) -> Chapter:
    """Helper to create a single chapter for testing."""
    chapter = Chapter(
        media_id=media_id,
        chapter_number=chapter_number,
        title=title,
    )
    db.add(chapter)
    await db.commit()
    await db.refresh(chapter)
    return chapter


# =========================================================================
# Auth required
# =========================================================================


@pytest.mark.asyncio
async def test_chapters_requires_auth():
    """Unauthenticated requests should be rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get(f"/api/v1/media/{uuid4()}/chapters")
        assert resp.status_code == 401, resp.text


# =========================================================================
# Empty state
# =========================================================================


@pytest.mark.asyncio
async def test_chapters_empty_state(auth_client: AsyncClient, db_session: AsyncSession):
    """Media with no chapters should return empty items."""
    media = await _create_test_media(db_session)

    resp = await auth_client.get(f"/api/v1/media/{media.id}/chapters")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["limit"] == 20
    assert body["offset"] == 0


# =========================================================================
# Success state — chapters exist
# =========================================================================


@pytest.mark.asyncio
async def test_chapters_returns_ordered_by_number(
    auth_client: AsyncClient, db_session: AsyncSession,
):
    """Chapters should be returned in ascending order by chapter_number."""
    media = await _get_first_media(db_session)

    await _seed_chapter(db_session, media.id, chapter_number=3.0, title="Ch3")
    await _seed_chapter(db_session, media.id, chapter_number=1.0, title="Ch1")
    await _seed_chapter(db_session, media.id, chapter_number=2.5, title="Ch2.5")

    resp = await auth_client.get(f"/api/v1/media/{media.id}/chapters")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["total"] >= 3

    items = body["items"]
    ours = [i for i in items if i["title"] in ("Ch1", "Ch2.5", "Ch3")]
    assert len(ours) == 3

    numbers = [i["chapter_number"] for i in ours]
    assert numbers == sorted(numbers), f"Chapters not in ascending order: {numbers}"


@pytest.mark.asyncio
async def test_chapters_returns_correct_fields(
    auth_client: AsyncClient, db_session: AsyncSession,
):
    """Each chapter item should include the expected fields."""
    media = await _get_first_media(db_session)
    chapter = await _seed_chapter(db_session, media.id, chapter_number=1.0, title="Correct Fields")

    resp = await auth_client.get(f"/api/v1/media/{media.id}/chapters")
    assert resp.status_code == 200, resp.text

    items = resp.json()["items"]
    match = [i for i in items if i["id"] == str(chapter.id)]
    assert len(match) == 1

    item = match[0]
    assert item["chapter_number"] == 1.0
    assert item["title"] == "Correct Fields"
    assert "volume_number" in item
    assert "published_at" in item
    assert "mangadex_chapter_id" in item


# =========================================================================
# Pagination
# =========================================================================


@pytest.mark.asyncio
async def test_chapters_pagination(auth_client: AsyncClient, db_session: AsyncSession):
    """limit and offset should paginate results."""
    media = await _get_first_media(db_session)

    for i in range(1, 4):
        await _seed_chapter(db_session, media.id, chapter_number=float(i), title=f"Ch{i}")

    resp = await auth_client.get(f"/api/v1/media/{media.id}/chapters?limit=1&offset=0")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert len(body["items"]) == 1
    assert body["total"] >= 3

    resp2 = await auth_client.get(f"/api/v1/media/{media.id}/chapters?limit=1&offset=1")
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
async def test_chapters_rejects_invalid_limit(auth_client: AsyncClient):
    """limit out of range should return 422."""
    media_id = uuid4()
    resp = await auth_client.get(f"/api/v1/media/{media_id}/chapters?limit=0")
    assert resp.status_code == 422, resp.text

    resp = await auth_client.get(f"/api/v1/media/{media_id}/chapters?limit=101")
    assert resp.status_code == 422, resp.text


@pytest.mark.asyncio
async def test_chapters_rejects_negative_offset(auth_client: AsyncClient):
    """negative offset should return 422."""
    media_id = uuid4()
    resp = await auth_client.get(f"/api/v1/media/{media_id}/chapters?limit=-1")
    assert resp.status_code == 422, resp.text


# =========================================================================
# Non-existent media
# =========================================================================


@pytest.mark.asyncio
async def test_chapters_non_existent_media(auth_client: AsyncClient):
    """Non-existent media_id should return 200 with empty items."""
    fake_id = uuid4()
    resp = await auth_client.get(f"/api/v1/media/{fake_id}/chapters")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0
