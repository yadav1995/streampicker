import time
import json
import threading
import logging
from typing import Any, Optional, Dict
from app.config import settings

logger = logging.getLogger(__name__)

class SimpleCache:
    def __init__(self, default_ttl: int = 300, redis_url: Optional[str] = None):
        self.default_ttl = default_ttl
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self._redis_client = None

        if redis_url:
            try:
                import redis
                self._redis_client = redis.from_url(redis_url, decode_responses=True)
                self._redis_client.ping()
                logger.info(f"Connected to Redis cache at {redis_url}")
            except Exception as e:
                logger.warning(f"Could not connect to Redis ({e}). Falling back to in-memory cache.")
                self._redis_client = None

    def get(self, key: str) -> Optional[Any]:
        if self._redis_client:
            try:
                val = self._redis_client.get(key)
                if val:
                    self.hits += 1
                    return json.loads(val)
                self.misses += 1
                return None
            except Exception:
                pass  # Fallback to local memory

        with self._lock:
            entry = self._store.get(key)
            if not entry:
                self.misses += 1
                return None

            now = time.time()
            if entry["expires_at"] < now:
                del self._store[key]
                self.evictions += 1
                self.misses += 1
                return None

            self.hits += 1
            return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl_val = ttl if ttl is not None else self.default_ttl
        if self._redis_client:
            try:
                self._redis_client.setex(key, ttl_val, json.dumps(value))
                return
            except Exception:
                pass

        with self._lock:
            self._store[key] = {
                "value": value,
                "expires_at": time.time() + ttl_val,
                "created_at": time.time()
            }

    def delete(self, key: str) -> bool:
        if self._redis_client:
            try:
                return bool(self._redis_client.delete(key))
            except Exception:
                pass

        with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False

    def clear_prefix(self, prefix: str) -> int:
        if self._redis_client:
            try:
                keys = self._redis_client.keys(f"{prefix}*")
                if keys:
                    return self._redis_client.delete(*keys)
                return 0
            except Exception:
                pass

        with self._lock:
            keys_to_delete = [k for k in self._store if k.startswith(prefix)]
            for k in keys_to_delete:
                del self._store[k]
            return len(keys_to_delete)

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total_requests = self.hits + self.misses
            hit_ratio = round((self.hits / total_requests * 100), 1) if total_requests > 0 else 0.0
            return {
                "active_entries": len(self._store),
                "is_redis_enabled": self._redis_client is not None,
                "hits": self.hits,
                "misses": self.misses,
                "total_requests": total_requests,
                "hit_ratio_percent": hit_ratio,
                "evictions": self.evictions
            }

# Global cache instance
cache = SimpleCache(default_ttl=settings.CACHE_DEFAULT_TTL, redis_url=settings.REDIS_URL)
