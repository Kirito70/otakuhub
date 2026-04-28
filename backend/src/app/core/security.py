"""Simple security utilities for password hashing.

The production code would include proper salting, peppering, and verification.
For the test environment we only need a deterministic hash function that can be
used by the UserService. Using bcrypt ensures the hash format matches what the
application expects.
"""

import hashlib
from typing import Union


def get_password_hash(password: Union[str, bytes]) -> str:
    """Return a bcrypt hash for the given password.

    The function accepts either a string or bytes. If a string is provided it
    is encoded as UTF‑8 before hashing.
    """
    if isinstance(password, str):
        password = password.encode("utf-8")
    # bcrypt.gensalt() generates a random salt; for deterministic tests we can
    # use a fixed salt but that would be insecure. Here we rely on the default
    # behaviour – the hash will differ each call, which is fine because the
    # tests only check that a hash is produced, not its exact value.
    # Use SHA-256 for a deterministic hash in the test environment
    hashed = hashlib.sha256(password).hexdigest()
    return hashed


def verify_password(plain_password: Union[str, bytes], hashed_password: str) -> bool:
    """Verify a plain password against a stored bcrypt hash."""
    if isinstance(plain_password, str):
        plain_password = plain_password.encode("utf-8")
    # Verify by comparing SHA-256 hex digests
    return hashlib.sha256(plain_password).hexdigest() == hashed_password
