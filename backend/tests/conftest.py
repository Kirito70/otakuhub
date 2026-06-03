import sys
import os
import tempfile
from uuid import uuid4

# Must be set BEFORE any app imports
os.environ.setdefault("JWT_SECRET", uuid4().hex)
os.environ.setdefault("CORS_ORIGINS", "http://localhost:8080")
# Use a persistent temp file so in-memory database data survives engine
# dispose and reconnect.  Cleaned up by the OS when the test process exits.
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{tempfile.mktemp(suffix='.db')}")

_ADMIN_USERNAME = "test_root_admin"
_ADMIN_PASSWORD = "TestRoot123!"

import pytest
from httpx import AsyncClient

# Ensure backend/src/ is on sys.path for `from src.app...` imports
SRC = os.path.abspath(os.path.join(__file__, '..', '..', 'src'))
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from src.app.main import app


def pytest_sessionstart() -> None:
    """Bootstrap admin with KNOWN credentials once per session.

    Because tests use SQLite :memory: (destroyed on engine dispose), we seed
    the admin user directly into the module-level engine WITHOUT triggering the
    app lifespan so the database persists across all TestClient instances.
    """
    import asyncio

    from src.app.database import connect_db, engine
    from src.app.services.auth_service import AuthService
    from sqlalchemy.ext.asyncio import AsyncSession

    async def _seed():
        from uuid import uuid4
        from src.app.models.media_entry import MediaEntry
        from sqlmodel import select

        await connect_db()  # creates tables (idempotent)
        async with AsyncSession(engine) as session:
            svc = AuthService()
            try:
                await svc.bootstrap_super_admin(
                    db=session,
                    username=_ADMIN_USERNAME,
                    email="root@test.local",
                    password=_ADMIN_PASSWORD,
                )
            except Exception:
                pass  # 409 = already bootstrapped (OK)

            # Seed a few media entries so integration tests don't fail
            result = await session.execute(select(MediaEntry).limit(1))
            existing = result.scalar_one_or_none()
            if existing is None:
                for title in ("Naruto", "One Piece", "Attack on Titan"):
                    entry = MediaEntry(
                        id=uuid4(),
                        title_romaji=title,
                        title_english=title,
                        media_type="anime",
                        format="TV",
                        status="finished",
                        average_score=7.5,
                    )
                    session.add(entry)
                await session.commit()

    asyncio.run(_seed())





@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Return dummy Authorization headers for unit tests that don't need real auth."""
    return {"Authorization": "Bearer test-mode-token"}


@pytest.fixture
async def db_session():
    """Provide a real async database session for integration tests.

    By default uses the in-memory SQLite configured via env var.
    Callers receive an async generator that cleans up on teardown.
    """
    from src.app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        yield session
