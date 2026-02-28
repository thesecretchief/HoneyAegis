"""Tests for the response cache service."""

import time
from app.services.cache_service import ResponseCache


class TestResponseCache:
    """Test in-memory LRU cache with TTL."""

    def test_set_and_get(self):
        cache = ResponseCache()
        cache.set("key1", {"data": "hello"})
        assert cache.get("key1") == {"data": "hello"}

    def test_get_missing_key(self):
        cache = ResponseCache()
        assert cache.get("nonexistent") is None

    def test_ttl_expiration(self):
        cache = ResponseCache(default_ttl=0)
        cache.set("key1", "value1", ttl=0)
        time.sleep(0.01)
        assert cache.get("key1") is None

    def test_custom_ttl(self):
        cache = ResponseCache(default_ttl=1)
        cache.set("key1", "value1", ttl=60)
        assert cache.get("key1") == "value1"

    def test_invalidate(self):
        cache = ResponseCache()
        cache.set("key1", "value1")
        cache.invalidate("key1")
        assert cache.get("key1") is None

    def test_invalidate_prefix(self):
        cache = ResponseCache()
        cache.set("stats:tenant1", "data1")
        cache.set("stats:tenant2", "data2")
        cache.set("sessions:tenant1", "data3")
        cache.invalidate_prefix("stats:")
        assert cache.get("stats:tenant1") is None
        assert cache.get("stats:tenant2") is None
        assert cache.get("sessions:tenant1") == "data3"

    def test_clear(self):
        cache = ResponseCache()
        cache.set("key1", "v1")
        cache.set("key2", "v2")
        cache.clear()
        assert cache.size == 0
        assert cache.get("key1") is None

    def test_max_entries_eviction(self):
        cache = ResponseCache(max_entries=3)
        cache.set("key1", "v1")
        cache.set("key2", "v2")
        cache.set("key3", "v3")
        cache.set("key4", "v4")  # Should evict key1
        assert cache.get("key1") is None
        assert cache.get("key4") == "v4"
        assert cache.size == 3

    def test_lru_ordering(self):
        cache = ResponseCache(max_entries=3)
        cache.set("key1", "v1")
        cache.set("key2", "v2")
        cache.set("key3", "v3")
        # Access key1 to make it recently used
        cache.get("key1")
        # Add key4, should evict key2 (least recently used)
        cache.set("key4", "v4")
        assert cache.get("key1") == "v1"
        assert cache.get("key2") is None

    def test_overwrite_existing_key(self):
        cache = ResponseCache()
        cache.set("key1", "old")
        cache.set("key1", "new")
        assert cache.get("key1") == "new"
        assert cache.size == 1

    def test_size_property(self):
        cache = ResponseCache()
        assert cache.size == 0
        cache.set("key1", "v1")
        assert cache.size == 1
        cache.set("key2", "v2")
        assert cache.size == 2
