"""Base service class for OtakuHub backend services."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.database import AsyncSessionLocal


class BaseService:
    """Base service class with common functionality."""

    def __init__(self, db_session: Optional[AsyncSession] = None):
        self._db_session = db_session

    @property
    def db_session(self) -> AsyncSession:
        """Get database session, create a new one if needed."""
        if self._db_session is None:
            # Create a new session and cache it so subsequent calls reuse the same session
            self._db_session = AsyncSessionLocal()
        return self._db_session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._db_session is None and hasattr(self, '_db_session'):
            # Clean up session if we created it
            await self._db_session.close()
