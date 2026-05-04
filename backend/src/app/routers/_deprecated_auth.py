"""Authentication routes for OtakuHub."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.services.auth_service import auth_service
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, LogoutResponse
from app.schemas.user import UserProfile
from app.core.security import verify_jwt_token
from app.core.auth import get_current_user as get_current_user_dep


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """User login endpoint."""
    try:
        token_response = await auth_service.login(db, login_request)
        return token_response
    except Exception as e:
        # Handle authentication errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e) if str(e) else "Invalid credentials"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    refresh_request: RefreshRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Refresh access token using refresh token."""
    try:
        token_response = await auth_service.refresh(db, refresh_request)
        return token_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e) if str(e) else "Invalid refresh token"
        )


@router.post("/logout")
async def logout(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
) -> LogoutResponse:
    """Logout user by revoking refresh token."""
    # For now we accept the refresh token in body
    # In a real implementation, we could make it require authorization
    # to make this more secure
    
    try:
        await auth_service.logout(db, refresh_token)
        return LogoutResponse(success=True)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e) if str(e) else "Logout failed"
        )


@router.post("/register")
async def register(
    username: str,
    email: str,
    password: str,
    db: AsyncSession = Depends(get_db)
) -> UserProfile:
    """User registration endpoint."""
    try:
        # Create user with registration
        user = await auth_service.register_user(db, username, email, password)
        
        # Return user profile (without sensitive info like password_hash)
        return UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            timezone=user.timezone,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    except Exception as e:
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed"
        )


# This endpoint will be used to test if user authentication works
@router.get("/me", response_model=UserProfile)
async def get_current_user(
    current_user = Depends(get_current_user_dep)
) -> UserProfile:
    """Get current user profile."""
    # This is a placeholder - we'll implement proper auth dependency in next step
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")