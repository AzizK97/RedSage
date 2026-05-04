import json
import os
from typing import Any

import redis.asyncio as client

redis_client = client.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6380)),
    decode_responses=True
)

async def get_cached(key: str) -> Any | None:
    """Get data from Redis cache."""
    data = await redis_client.get(key)
    return json.loads(data) if data else None

async def set_cached(key: str, value: Any, ttl_seconds: int = 300):
    """Save data to Redis cache with TTL (default 5 minutes)."""
    await redis_client.set(key, json.dumps(value), ex=ttl_seconds)

async def close_redis():
    await redis_client.close()


# --- Synchronous helpers (convenience wrappers for sync callers) ---
try:
    import redis as sync_redis
except Exception:
    sync_redis = None

def get_cached_sync(key: str):
    """Synchronous get from Redis. Returns parsed JSON or None."""
    if sync_redis is None:
        return None
    try:
        client_sync = sync_redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6380)),
            decode_responses=True,
        )
        data = client_sync.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None

def set_cached_sync(key: str, value, ttl_seconds: int = 3600):
    """Synchronous set with TTL."""
    if sync_redis is None:
        return
    try:
        client_sync = sync_redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6380)),
            decode_responses=True,
        )
        client_sync.setex(key, ttl_seconds, json.dumps(value))
    except Exception:
        return