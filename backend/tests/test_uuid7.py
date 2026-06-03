"""Tests for generate_uuid7()."""

from uuid import UUID

from src.app.core.uuid7 import generate_uuid7


def test_returns_uuid_instance():
    """generate_uuid7() should return a UUID instance."""
    uid = generate_uuid7()
    assert isinstance(uid, UUID)


def test_version_is_7():
    """RFC 9562 UUID v7 has version field set to 7."""
    uid = generate_uuid7()
    assert uid.version == 7, f"Expected version 7, got {uid.version}"


def test_variant_is_rfc():
    """RFC 9562 variant should be 0b10 (RFC 4122 / RFC 9562)."""
    uid = generate_uuid7()
    # variant 0b10 = RFC 4122 (int value 2)
    assert uid.variant == UUID("00000000-0000-0000-8000-000000000000").variant


def test_unique_values():
    """Multiple calls should generate different UUIDs."""
    uuids = {generate_uuid7() for _ in range(100)}
    assert len(uuids) == 100


def test_monotonic_timestamps():
    """UUIDs generated in sequence should have increasing timestamps."""
    uuids = [generate_uuid7() for _ in range(100)]
    # UUID v7 embeds timestamp in the first 48 bits (6 bytes)
    # Random bits after the timestamp can vary, so only compare the time portion
    for i in range(1, len(uuids)):
        ts_prev = int.from_bytes(uuids[i - 1].bytes[:6], byteorder="big")
        ts_curr = int.from_bytes(uuids[i].bytes[:6], byteorder="big")
        assert ts_curr >= ts_prev, (
            f"UUID timestamp at index {i} regressed: "
            f"{ts_curr} < {ts_prev}"
            f" (uuids: {uuids[i]} < {uuids[i - 1]})"
        )


def test_string_format():
    """UUID v7 string should match standard UUID format."""
    uid = generate_uuid7()
    s = str(uid)
    assert len(s) == 36
    assert s.count("-") == 4
    # Version digit should be '7' at position 14
    assert s[14] == "7", f"Version digit should be 7, got {s[14]}"


def test_time_extraction():
    """We should be able to extract the embedded timestamp."""
    before_ms = int(__import__("time").time() * 1000)
    uid = generate_uuid7()
    after_ms = int(__import__("time").time() * 1000)

    # Extract the first 6 bytes (48-bit timestamp)
    timestamp_ms = int.from_bytes(uid.bytes[:6], byteorder="big")

    assert before_ms <= timestamp_ms <= after_ms + 10, (
        f"Timestamp {timestamp_ms} outside range [{before_ms}, {after_ms}]"
    )
