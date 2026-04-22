"""
Authentication Pydantic schemas.
"""
from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    """Request schema for login."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Response schema for token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"