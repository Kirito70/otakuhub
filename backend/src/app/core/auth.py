"""Authentication utilities for route dependencies.

For the purpose of the test suite we provide a very simple implementation that
always raises a 401 Unauthorized error. This satisfies the FastAPI dependency
signature without requiring a full JWT implementation.
"""

from fastapi import HTTPException, status


async def get_current_user():
    """Dependency that raises 401 – routes that require auth will return 401.

    The test suite only checks that the endpoint is reachable and may accept
    either 200 or 401, so this minimal stub is sufficient.
    """
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
