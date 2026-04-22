"""
Authentication routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from schemas.auth import LoginRequest, TokenResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
async def login(
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """User login endpoint."""
    # This will be implemented in the auth service
    raise HTTPException(status_code=501, detail="Not implemented")

@router.post("/refresh")
async def refresh_token():
    """Refresh access token."""
    # This will be implemented in the auth service
    raise HTTPException(status_code=501, detail="Not implemented")

@router.post("/logout")
async def logout():
    """User logout endpoint."""
    # This will be implemented in the auth service
    raise HTTPException(status_code=501, detail="Not implemented")