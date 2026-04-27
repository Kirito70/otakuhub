"""Pydantic schemas for authentication endpoints."""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, constr


class LoginRequest(BaseModel):
    """Payload for ``POST /auth/login``.

    ``username`` can be either the user's ``username`` or ``email`` – the service
    will resolve it accordingly.
    """

    model_config = ConfigDict(from_attributes=True)

    username: constr(min_length=1, max_length=50)
    password: constr(min_length=8)


class RefreshRequest(BaseModel):
    """Payload for ``POST /auth/refresh`` – client sends the stored refresh token."""

    model_config = ConfigDict(from_attributes=True)

    refresh_token: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Response containing a new access token and refresh token."""

    model_config = ConfigDict(from_attributes=True)

    access_token: str
    refresh_token: str
    expires_in: int  # seconds until access token expiry


class LogoutResponse(BaseModel):
    """Simple success payload for ``POST /auth/logout``."""

    model_config = ConfigDict(from_attributes=True)

    success: bool = True
