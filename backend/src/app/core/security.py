"""Security utilities used by auth service."""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Union, Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from src.app.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _to_str_password(password: Union[str, bytes]) -> str:
    if isinstance(password, bytes):
        return password.decode("utf-8")
    return password


def _is_legacy_sha256_hash(hashed_password: str) -> bool:
    return len(hashed_password) == 64 and all(c in "0123456789abcdef" for c in hashed_password)


def _legacy_sha256_hash(password: Union[str, bytes]) -> str:
    raw = password if isinstance(password, bytes) else password.encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def get_password_hash(password: Union[str, bytes]) -> str:
    """Hash a password with bcrypt/passlib policy."""
    return _pwd_context.hash(_to_str_password(password))


def verify_password(plain_password: Union[str, bytes], hashed_password: str) -> bool:
    """Verify plain password against stored hash (bcrypt + legacy sha256 fallback)."""
    if _is_legacy_sha256_hash(hashed_password):
        return _legacy_sha256_hash(plain_password) == hashed_password
    return _pwd_context.verify(_to_str_password(plain_password), hashed_password)


def needs_password_rehash(hashed_password: str) -> bool:
    """Whether stored hash should be upgraded to current password policy."""
    return _is_legacy_sha256_hash(hashed_password) or _pwd_context.needs_update(hashed_password)


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
