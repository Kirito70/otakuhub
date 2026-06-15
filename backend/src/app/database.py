"""Database configuration and connection management using SQLModel."""

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


async def connect_db() -> None:
    """Connect to the database, enable extensions, create tables, and stamp Alembic."""
    async with engine.begin() as conn:
        # Enable required PostgreSQL extensions before creating tables
        # pg_trgm enables trigram-based partial-match search (gin_trgm_ops indexes)
        # unaccent enables accent-insensitive text search
        # btree_gin enables GIN indexes on btree-compatible types
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gin"))
        await conn.commit()

    # Create all tables from SQLModel model definitions (idempotent — checkfirst=True)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Stamp Alembic to 'head' so future `alembic upgrade head` is a no-op
    # Uses raw SQL because Alembic's command.stamp() needs a sync driver URL.
    async with engine.begin() as conn:
        await conn.execute(text(
            "CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) PRIMARY KEY)"
        ))
        # Migration chain: 001 → 002 → 003. Head is currently '003'.
        await conn.execute(text(
            "INSERT INTO alembic_version (version_num) VALUES ('003') ON CONFLICT (version_num) DO NOTHING"
        ))
        await conn.commit()

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
