"""Test helper utilities"""

from smartmonkey.utils.helpers import calculate_hash, calculate_similarity


def test_calculate_hash():
    """Test hash calculation"""
    text = "test string"
    hash1 = calculate_hash(text)
    hash2 = calculate_hash(text)

    assert hash1 == hash2
    assert len(hash1) == 32  # MD5 hash length


def test_calculate_similarity():
    """Test string similarity"""
    # Identical strings
    assert calculate_similarity("test", "test") == 1.0

    # Different strings
    assert calculate_similarity("abc", "xyz") < 0.5

    # Empty strings
    assert calculate_similarity("", "") == 0.0
    assert calculate_similarity("test", "") == 0.0
