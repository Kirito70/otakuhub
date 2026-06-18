"""Database configuration and connection management using SQLModel."""

import asyncio
import functools
from pathlib import Path

from alembic import command
from alembic.config import Config as AlembicConfig
from sqlmodel import SQLModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.config import settings

# Create async database engine
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Set to True to see SQL queries
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
)

# Create async session maker
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncSession:
    """Get database session for dependency injection."""
    async with AsyncSessionLocal() as session:
        yield session


def _alembic_cfg() -> AlembicConfig:
    """Build an Alembic Config pointing at backend/alembic/."""
    backend_dir = Path(__file__).resolve().parent.parent.parent
    ini = backend_dir / "alembic.ini"
    cfg = AlembicConfig(str(ini))
    cfg.set_main_option("script_location", str(backend_dir / "alembic"))
    cfg.set_main_option("sqlalchemy.url", settings.database_url)
    return cfg


async def connect_db() -> None:
    """Connect to the database, enable extensions, and run pending Alembic migrations.

    Uses Alembic as the single source of truth for schema management (not
    ``SQLModel.metadata.create_all``) to avoid conflicts between DDL generated
    from model definitions and the incremental migration files.
    """
    # Only create PG extensions when connected to PostgreSQL
    if "postgresql" in engine.url.drivername:
        async with engine.begin() as conn:
            # Enable required PostgreSQL extensions before creating tables
            # pg_trgm enables trigram-based partial-match search (gin_trgm_ops indexes)
            # unaccent enables accent-insensitive text search
            # btree_gin enables GIN indexes on btree-compatible types
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent"))
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gin"))
            await conn.commit()

    # Drop old table name ``syncjob`` if it exists from a previous model
    # definition that did not have an explicit ``__tablename__``.
    if "postgresql" in engine.url.drivername:
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS syncjob CASCADE"))
            await conn.commit()

    # Run Alembic migrations from scratch or apply pending ones.
    # This is the single source of truth for the schema.
    # Alembic's command.upgrade() calls asyncio.run() internally (via env.py),
    # so it must run in a separate thread to avoid nesting event loops.
    cfg = _alembic_cfg()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, functools.partial(command.upgrade, cfg, "head"))

    print(f"Database connected: {settings.database_url.split('@')[-1]}")


async def disconnect_db() -> None:
    """Disconnect from the database."""
    await engine.dispose()
    print("Database disconnected")


async def check_db_connection() -> bool:
    """Check if database connection is healthy."""
    try:
        async with engine.begin() as conn:
            # Execute a simple query to check connection
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection check failed: {e}")
        return False
