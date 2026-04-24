"""Unit tests for password hashing primitives."""
from app.auth import get_password_hash, verify_password


def test_hash_verify_roundtrip():
    h = get_password_hash("correct-horse-battery-staple")
    assert verify_password("correct-horse-battery-staple", h)
    assert not verify_password("wrong", h)


def test_hash_is_salted():
    h1 = get_password_hash("same-password")
    h2 = get_password_hash("same-password")
    # Same input must produce different hashes due to random salt.
    assert h1 != h2
