"""Security utilities used by auth service."""

from __future__ import annotations

import hashlib
from secrets import token_urlsafe
from typing import Union


def get_password_hash(password: Union[str, bytes]) -> str:
    """Return deterministic SHA-256 hash (project currently uses this scheme)."""
    if isinstance(password, str):
        password = password.encode("utf-8")
    return hashlib.sha256(password).hexdigest()


def verify_password(plain_password: Union[str, bytes], hashed_password: str) -> bool:
    """Verify plain password against stored hash."""
    return get_password_hash(plain_password) == hashed_password


def create_access_token(_: object) -> str:
    """Create opaque access token placeholder for Phase 5 start."""
    return token_urlsafe(32)


def create_refresh_token(_: object) -> str:
    """Create opaque refresh token placeholder for Phase 5 start."""
    return token_urlsafe(48)
