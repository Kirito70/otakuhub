"""Base service class – holds an optional async DB session.

The real application would provide common utilities (e.g., transaction handling),
but for the test suite we only need a simple container for the session.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
