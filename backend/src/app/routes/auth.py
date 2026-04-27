"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.database import get_db_session
from src.app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """User login endpoint."""
    # Implementation will be in Phase 4
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/refresh")
async def refresh_token():
    """Refresh access token."""
    # Implementation will be in Phase 4
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/logout")
async def logout():
    """User logout endpoint."""
    # Implementation will be in Phase 4
    raise HTTPException(status_code=501, detail="Not implemented")
