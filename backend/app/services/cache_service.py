"""Lightweight in-memory response cache for HoneyAegis.

Provides a simple TTL-based cache for expensive API responses (stats, map data).
Uses an async-safe dictionary with automatic expiration.

For production deployments, this can be swapped with Redis caching.
"""

import logging
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_TTL = 15  # seconds
_MAX_ENTRIES = 500


@dataclass
class CacheEntry:
    """A single cached value with TTL."""

    value: Any
    expires_at: float


class ResponseCache:
    """Thread-safe in-memory LRU cache with TTL."""

    def __init__(self, max_entries: int = _MAX_ENTRIES, default_ttl: int = _DEFAULT_TTL):
        self._store: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_entries = max_entries
        self._default_ttl = default_ttl

    def get(self, key: str) -> Any | None:
        """Get a value from cache. Returns None if expired or missing."""
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.monotonic() > entry.expires_at:
            del self._store[key]
            return None
        # Move to end (LRU)
        self._store.move_to_end(key)
        return entry.value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store a value in cache with optional TTL override."""
        if key in self._store:
            del self._store[key]
        elif len(self._store) >= self._max_entries:
            self._store.popitem(last=False)

        self._store[key] = CacheEntry(
            value=value,
            expires_at=time.monotonic() + (ttl or self._default_ttl),
        )

    def invalidate(self, key: str) -> None:
        """Remove a specific key from cache."""
        self._store.pop(key, None)

    def invalidate_prefix(self, prefix: str) -> None:
        """Remove all keys matching a prefix."""
        keys_to_remove = [k for k in self._store if k.startswith(prefix)]
        for k in keys_to_remove:
            del self._store[k]

    def clear(self) -> None:
        """Clear the entire cache."""
        self._store.clear()

    @property
    def size(self) -> int:
        """Current number of entries in cache."""
        return len(self._store)


# Global cache instance
response_cache = ResponseCache()
