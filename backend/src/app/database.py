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
    """Connect to the database and create tables if they don't exist."""
    async with engine.begin() as conn:
        # Create all tables defined in SQLModel models
        await conn.run_sync(SQLModel.metadata.create_all)
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
