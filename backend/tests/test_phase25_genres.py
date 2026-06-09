"""Phase 25.5 integration tests: genre list endpoint.

Tests GET /api/v1/media/genres which returns all genres ordered by name.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.main import app
from src.app.database import AsyncSessionLocal
from src.app.models import Genre

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


async def _seed_genres(db: AsyncSession) -> list[Genre]:
    """Seed a few genres for testing if none exist."""
    result = await db.exec(select(Genre).limit(1))
    existing = result.one_or_none()
    if existing:
        return []  # Let tests use whatever genres exist

    genres = [
        Genre(name="Action", slug="action"),
        Genre(name="Comedy", slug="comedy"),
        Genre(name="Drama", slug="drama"),
    ]
    for g in genres:
        db.add(g)
    await db.commit()
    for g in genres:
        await db.refresh(g)
    return genres


# =========================================================================
# Auth required
# =========================================================================


@pytest.mark.asyncio
async def test_genres_requires_auth():
    """Unauthenticated requests should be rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/media/genres")
        assert resp.status_code == 401, resp.text


# =========================================================================
# Returns all genres ordered by name
# =========================================================================


@pytest.mark.asyncio
async def test_genres_returns_ordered_by_name(
    auth_client: AsyncClient, db_session: AsyncSession,
):
    """Genres should be returned ordered alphabetically by name."""
    await _seed_genres(db_session)

    resp = await auth_client.get("/api/v1/media/genres")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert "items" in body
    items = body["items"]
    assert len(items) >= 1

    # Verify ordering by name
    names = [g["name"] for g in items]
    assert names == sorted(names), f"Genres not sorted: {names}"


# =========================================================================
# Correct fields
# =========================================================================


@pytest.mark.asyncio
async def test_genres_returns_correct_fields(
    auth_client: AsyncClient, db_session: AsyncSession,
):
    """Each genre should have id, name, and slug fields."""
    seeded = await _seed_genres(db_session)

    resp = await auth_client.get("/api/v1/media/genres")
    assert resp.status_code == 200, resp.text

    items = resp.json()["items"]
    assert len(items) >= 1

    genre = items[0]
    assert "id" in genre
    assert "name" in genre
    assert "slug" in genre
