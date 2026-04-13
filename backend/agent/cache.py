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