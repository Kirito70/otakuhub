"""RFC 9562 UUID v7 generation.

UUID v7 features a Unix timestamp in milliseconds (48 bits) followed by
random data (74 bits). This provides:
- Time-ordered values (good for B-tree index performance)
- 1 million+ unique values per second with negligible collision risk
- Portability across PostgreSQL and SQLite (no pg_uuidv7 extension required)

Implementation adapted from the UUID draft specification:
https://www.ietf.org/rfc/rfc9562.html
"""

import os
import time
from uuid import UUID


def generate_uuid7() -> UUID:
    """Generate a UUID v7 according to RFC 9562.

    Format (128 bits):
      - 48 bits: Unix timestamp in milliseconds
      -  4 bits: version (0b0111 = 7)
      - 12 bits: random (sub-millisecond sequencing)
      -  2 bits: variant (0b10)
      - 62 bits: random

    Returns:
        A time-ordered UUID v7 instance.
    """
    # Get current timestamp in milliseconds
    timestamp_ms = int(time.time() * 1000)

    # Generate 10 random bytes (80 bits)
    random_bytes = os.urandom(10)

    # Build the UUID parts
    # Bytes 0-5: timestamp (48 bits, big-endian)
    # Bytes 6-15: random (80 bits)
    time_bytes = timestamp_ms.to_bytes(6, byteorder="big")

    # Combine: 6 bytes time + 10 bytes random = 16 bytes
    raw = bytearray(time_bytes) + bytearray(random_bytes)

    # Set version (bits 48-51): 0b0111 = version 7
    raw[6] = (raw[6] & 0x0F) | 0x70

    # Set variant (bits 64-65): 0b10 = RFC 9562 variant
    raw[8] = (raw[8] & 0x3F) | 0x80

    return UUID(bytes=bytes(raw))
