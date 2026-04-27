import json
import os
from typing import Any

import redis

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6380)),
    decode_responses=True
)

def get_cached(key: str) -> Any | None:
    """Get data from Redis cache."""
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None

def set_cached(key: str, value: Any, ttl_seconds: int = 300):
    """Save data to Redis cache with TTL (default 5 minutes)."""
    try:
        redis_client.set(key, json.dumps(value), ex=ttl_seconds)
    except Exception:
        pass

async def aget_cached(key: str) -> Any | None:
    """Async get data from Redis cache."""
    import redis.asyncio as aclient
    aredis_client = aclient.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6380)),
        decode_responses=True
    )
    try:
        data = await aredis_client.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None

async def aset_cached(key: str, value: Any, ttl_seconds: int = 300):
    """Async save data to Redis cache with TTL (default 5 minutes)."""
    import redis.asyncio as aclient
    aredis_client = aclient.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6380)),
        decode_responses=True
    )
    try:
        await aredis_client.set(key, json.dumps(value), ex=ttl_seconds)
    except Exception:
        pass