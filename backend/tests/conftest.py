"""
Test configuration and fixtures.
"""
import pytest
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine, AsyncSessionLocal


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    import asyncio
    loop = asyncio.get_event_loop()
    yield loop


@pytest.fixture(scope="session")
async def db_engine():
    """Create a database engine for testing."""
    return engine


@pytest.fixture(scope="function")
async def db_session():
    """Create a database session for each test function."""
    async with AsyncSessionLocal() as session:
        yield session