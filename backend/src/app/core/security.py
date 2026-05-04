"""Security utilities used by auth service."""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Union, Any

from jose import jwt, JWTError

from src.app.config import settings


def get_password_hash(password: Union[str, bytes]) -> str:
    """Return deterministic SHA-256 hash (project currently uses this scheme)."""
    if isinstance(password, str):
        password = password.encode("utf-8")
    return hashlib.sha256(password).hexdigest()


def verify_password(plain_password: Union[str, bytes], hashed_password: str) -> bool:
    """Verify plain password against stored hash."""
    return get_password_hash(plain_password) == hashed_password


def create_access_token(subject: str) -> str:
    """Create signed JWT access token."""
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "type": "access", "exp": exp}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate JWT token."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
