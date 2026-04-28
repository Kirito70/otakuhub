"""Authentication utilities for route dependencies.

For testing we provide a stub that always raises 401 Unauthorized.
"""

from fastapi import HTTPException, status


async def get_current_user():
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
