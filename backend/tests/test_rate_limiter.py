"""Tests for rate limiting service."""

import pytest

from app.services.rate_limiter import TokenBucket


def test_token_bucket_allows_within_capacity():
    """TokenBucket allows requests within capacity."""
    bucket = TokenBucket(capacity=10, refill_rate=1)
    for _ in range(10):
        assert bucket.consume() is True


def test_token_bucket_blocks_over_capacity():
    """TokenBucket blocks requests over capacity."""
    bucket = TokenBucket(capacity=3, refill_rate=0.1)
    # Consume all tokens
    for _ in range(3):
        bucket.consume()
    # Next should be blocked
    assert bucket.consume() is False


def test_token_bucket_refills():
    """TokenBucket refills tokens over time."""
    import time

    bucket = TokenBucket(capacity=2, refill_rate=100)  # 100 tokens/sec
    bucket.consume()
    bucket.consume()
    assert bucket.consume() is False

    # Wait briefly for refill
    time.sleep(0.05)  # 50ms → should get ~5 tokens
    assert bucket.consume() is True


def test_token_bucket_never_exceeds_capacity():
    """TokenBucket tokens never exceed capacity."""
    import time

    bucket = TokenBucket(capacity=5, refill_rate=1000)
    time.sleep(0.1)  # Should refill way more than 5

    # Can consume exactly capacity
    for _ in range(5):
        assert bucket.consume() is True

    # Next should fail (back to 0)
    assert bucket.consume() is False


def test_token_bucket_partial_consume():
    """TokenBucket supports consuming multiple tokens at once."""
    bucket = TokenBucket(capacity=10, refill_rate=1)
    assert bucket.consume(5) is True
    assert bucket.consume(5) is True
    assert bucket.consume(1) is False


def test_token_bucket_zero_capacity():
    """TokenBucket with zero capacity blocks everything."""
    bucket = TokenBucket(capacity=0, refill_rate=1)
    assert bucket.consume() is False
