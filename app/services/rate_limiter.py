import time
import threading
from typing import Dict, Tuple, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

class TokenBucketRateLimiter:
    def __init__(self, requests_per_minute: int = 180, burst_limit: int = 60):
        self.rate = requests_per_minute / 60.0  # tokens per second
        self.capacity = burst_limit
        self._buckets: Dict[str, Tuple[float, float]] = {}  # ip -> (tokens, last_update)
        self._lock = threading.Lock()

    def is_allowed(self, client_id: str) -> Tuple[bool, int, int]:
        with self._lock:
            now = time.time()
            if client_id not in self._buckets:
                self._buckets[client_id] = (self.capacity - 1, now)
                return True, int(self.capacity - 1), 60

            tokens, last_update = self._buckets[client_id]
            # Refill tokens
            elapsed = now - last_update
            tokens = min(self.capacity, tokens + elapsed * self.rate)

            if tokens >= 1.0:
                self._buckets[client_id] = (tokens - 1.0, now)
                remaining = int(tokens - 1.0)
                return True, remaining, 60
            else:
                self._buckets[client_id] = (tokens, now)
                reset_after = max(1, int((1.0 - tokens) / self.rate))
                return False, 0, reset_after

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 180, burst_limit: int = 60):
        super().__init__(app)
        self.limiter = TokenBucketRateLimiter(requests_per_minute, burst_limit)

    async def dispatch(self, request: Request, call_next):
        # Skip static assets and root
        path = request.url.path
        if path.startswith("/static") or path in ["/", "/favicon.ico"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown_client"
        allowed, remaining, reset_after = self.limiter.is_allowed(client_ip)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please slow down your requests.",
                    "retry_after_seconds": reset_after
                },
                headers={
                    "X-RateLimit-Limit": str(self.limiter.capacity),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_after),
                    "Retry-After": str(reset_after)
                }
            )

        response: Response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.limiter.capacity)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_after)
        return response
