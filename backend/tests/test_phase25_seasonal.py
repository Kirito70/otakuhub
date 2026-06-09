"""Phase 25.6 integration tests: seasonal media endpoint.

Tests GET /api/v1/media/seasonal which returns media for a given season
ordered by average score descending.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.main import app
from src.app.database import AsyncSessionLocal
from src.app.models import MediaEntry

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


async def _seed_seasonal_media(db: AsyncSession) -> None:
    """Seed a set of seasonal media entries for testing."""
    from datetime import datetime, timezone

    entries = [
        MediaEntry(
            id=uuid4(),
            title_romaji="Best Show",
            media_type="anime",
            format="TV",
            status="releasing",
            season_year=2026,
            season="spring",
            average_score=9.5,
            popularity=1000,
            episode_count=12,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        MediaEntry(
            id=uuid4(),
            title_romaji="Good Show",
            media_type="anime",
            format="TV",
            status="releasing",
            season_year=2026,
            season="spring",
            average_score=8.0,
            popularity=800,
            episode_count=24,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        MediaEntry(
            id=uuid4(),
            title_romaji="Decent Show",
            media_type="anime",
            format="TV",
            status="releasing",
            season_year=2026,
            season="spring",
            average_score=6.5,
            popularity=500,
            episode_count=12,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        MediaEntry(
            id=uuid4(),
            title_romaji="Unscored Show",
            media_type="anime",
            format="TV",
            status="releasing",
            season_year=2026,
            season="spring",
            average_score=None,
            popularity=300,
            episode_count=12,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        # Different season — should not appear in spring 2026 results
        MediaEntry(
            id=uuid4(),
            title_romaji="Summer Show",
            media_type="anime",
            format="TV",
            status="releasing",
            season_year=2026,
            season="summer",
            average_score=9.0,
            popularity=900,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]
    for entry in entries:
        db.add(entry)
    await db.commit()


# =========================================================================
# Auth required
# =========================================================================


@pytest.mark.asyncio
async def test_seasonal_requires_auth():
    """Unauthenticated requests should be rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/media/seasonal")
        assert resp.status_code == 401, resp.text


# =========================================================================
# Returns empty for no matching media
# =========================================================================


@pytest.mark.asyncio
async def test_seasonal_empty_when_no_data(auth_client: AsyncClient):
    """Querying for a season with no media should return empty items."""
    resp = await auth_client.get("/api/v1/media/seasonal?season_year=1999&season=spring")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0


# =========================================================================
# Ordered by score descending
# =========================================================================


@pytest.mark.asyncio
async def test_seasonal_ordered_by_score_desc(
    auth_client: AsyncClient, db_session: AsyncSession,
):
    """Items should be ordered by average_score descending (NULLS LAST)."""
    await _seed_seasonal_media(db_session)

    resp = await auth_client.get("/api/v1/media/seasonal?season_year=2026&season=spring")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    items = body["items"]
    assert len(items) >= 3
    assert body["total"] >= 4

    # Verify order: Best (9.5), Good (8.0), Decent (6.5), then Unscored (null)
    scores = [i["average_score"] for i in items if i["average_score"] is not None]
    assert scores == sorted(scores, reverse=True), "Scores not in descending order"

    # Check that null-scored items come last
    non_null_scores = [i for i in items if i["average_score"] is not None]
    null_scores = [i for i in items if i["average_score"] is None]
    if null_scores:
        last_non_null_idx = max(
            items.index(i) for i in non_null_scores
        ) if non_null_scores else -1
        first_null_idx = min(
            items.index(i) for i in null_scores
        ) if null_scores else len(items)
        assert first_null_idx > last_non_null_idx, (
            "Null-scored items should come after scored items"
        )


# =========================================================================
# Correct fields
# =========================================================================


@pytest.mark.asyncio
async def test_seasonal_returns_correct_fields(
    auth_client: AsyncClient, db_session: AsyncSession,
):
    """Each item should have the expected seasonal media fields."""
    await _seed_seasonal_media(db_session)

    resp = await auth_client.get("/api/v1/media/seasonal?season_year=2026&season=spring")
    assert resp.status_code == 200, resp.text

    items = resp.json()["items"]
    assert len(items) >= 1

    item = items[0]
    assert "id" in item
    assert "title_romaji" in item
    assert "average_score" in item
    assert "season" in item
    assert "season_year" in item
    assert "media_type" in item
    assert "format" in item
    assert "status" in item


# =========================================================================
# Pagination
# =========================================================================


@pytest.mark.asyncio
async def test_seasonal_pagination(
    auth_client: AsyncClient, db_session: AsyncSession,
):
    """limit and offset should paginate results."""
    await _seed_seasonal_media(db_session)

    resp = await auth_client.get("/api/v1/media/seasonal?season_year=2026&season=spring&limit=2&offset=0")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert len(body["items"]) == 2
    assert body["limit"] == 2
    assert body["offset"] == 0
    assert body["total"] >= 4

    # Verify different page
    first_page_ids = {i["id"] for i in body["items"]}

    resp2 = await auth_client.get("/api/v1/media/seasonal?season_year=2026&season=spring&limit=2&offset=2")
    assert resp2.status_code == 200, resp2.text
    body2 = resp2.json()
    assert len(body2["items"]) >= 1

    second_page_ids = {i["id"] for i in body2["items"]}
    assert first_page_ids.isdisjoint(second_page_ids), (
        "Pages should not overlap"
    )


# =========================================================================
# Invalid parameters
# =========================================================================


@pytest.mark.asyncio
async def test_seasonal_rejects_invalid_limit(auth_client: AsyncClient):
    """limit out of range should return 422."""
    resp = await auth_client.get("/api/v1/media/seasonal?limit=0")
    assert resp.status_code == 422, resp.text

    resp = await auth_client.get("/api/v1/media/seasonal?limit=101")
    assert resp.status_code == 422, resp.text


@pytest.mark.asyncio
async def test_seasonal_rejects_negative_offset(auth_client: AsyncClient):
    """Negative offset should return 422."""
    resp = await auth_client.get("/api/v1/media/seasonal?offset=-1")
    assert resp.status_code == 422, resp.text
