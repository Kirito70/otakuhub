"""Authentication routes."""

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.database import get_db_session
from src.app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, LogoutResponse
from src.app.schemas.user import UserProfile
from src.app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserProfile, status_code=201)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db_session),
):
    user = await auth_service.register(db, payload)
    return UserProfile.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
):
    return await auth_service.login(db, login_request)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshRequest,
    db: AsyncSession = Depends(get_db_session),
):
    return await auth_service.refresh(db, refresh_request)


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    refresh_request: RefreshRequest,
    db: AsyncSession = Depends(get_db_session),
):
    await auth_service.logout(db, refresh_request.refresh_token)
    return LogoutResponse(success=True)
