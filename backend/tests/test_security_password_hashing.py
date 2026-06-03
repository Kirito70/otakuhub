from __future__ import annotations

import hashlib

from src.app.core.security import get_password_hash, needs_password_rehash, verify_password


def test_bcrypt_hash_and_verify_roundtrip() -> None:
    password = "MyS3curePass!"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert needs_password_rehash(hashed) is False


def test_legacy_sha256_hash_still_verifies_and_flags_rehash() -> None:
    password = "legacy-pass"
    legacy_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    assert verify_password(password, legacy_hash) is True
    assert needs_password_rehash(legacy_hash) is True
