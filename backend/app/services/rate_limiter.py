"""Rate limiting middleware for HoneyAegis API.

Token-bucket rate limiter backed by in-memory storage.
Configurable per-endpoint and global limits via env vars:
  RATE_LIMIT_GLOBAL_CAPACITY (default: 100)
  RATE_LIMIT_GLOBAL_REFILL (default: 10 tokens/sec)
  RATE_LIMIT_AUTH_CAPACITY (default: 10)
  RATE_LIMIT_AUTH_REFILL (default: 1 token/sec)
"""

import time
import logging
from collections import defaultdict
from dataclasses import dataclass, field

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class TokenBucket:
    """Token bucket rate limiter for a single key."""

    capacity: float
    refill_rate: float  # tokens per second
    tokens: float = field(init=False)
    last_refill: float = field(init=False)

    def __post_init__(self):
        self.tokens = self.capacity
        self.last_refill = time.monotonic()

    def consume(self, tokens: float = 1.0) -> bool:
        """Attempt to consume tokens. Returns True if allowed."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


# Global rate limit store (per IP) — configurable via RATE_LIMIT_GLOBAL_*
_buckets: dict[str, TokenBucket] = defaultdict(
    lambda: TokenBucket(
        capacity=settings.rate_limit_global_capacity,
        refill_rate=settings.rate_limit_global_refill,
    )
)

# Auth endpoint rate limit (stricter) — configurable via RATE_LIMIT_AUTH_*
_auth_buckets: dict[str, TokenBucket] = defaultdict(
    lambda: TokenBucket(
        capacity=settings.rate_limit_auth_capacity,
        refill_rate=settings.rate_limit_auth_refill,
    )
)


def _get_client_ip(request: Request) -> str:
    """Extract client IP from request, respecting X-Forwarded-For."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip rate limiting for health/metrics endpoints
        path = request.url.path
        if path in ("/health", "/metrics"):
            return await call_next(request)

        client_ip = _get_client_ip(request)

        # Stricter limits for auth endpoints
        if path.startswith("/api/v1/auth"):
            bucket = _auth_buckets[client_ip]
            if not bucket.consume():
                logger.warning("Auth rate limit exceeded for IP: %s", client_ip)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many authentication attempts. Please wait.",
                    headers={"Retry-After": "60"},
                )
        else:
            bucket = _buckets[client_ip]
            if not bucket.consume():
                logger.warning("Rate limit exceeded for IP: %s", client_ip)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please slow down.",
                    headers={"Retry-After": "10"},
                )

        response = await call_next(request)
        return response
