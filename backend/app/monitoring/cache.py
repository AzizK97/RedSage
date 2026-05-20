import json
from datetime import date, datetime
from typing import Any

import redis.asyncio as redis

from app.core.config import settings


class MonitoringCache:
    def __init__(self) -> None:
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def close(self) -> None:
        await self.client.close()

    async def acquire_lock(self, key: str, ttl_seconds: int) -> bool:
        return bool(await self.client.set(key, "1", ex=ttl_seconds, nx=True))

    async def release_lock(self, key: str) -> None:
        await self.client.delete(key)

    async def get_json(self, key: str) -> Any | None:
        raw = await self.client.get(key)
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    async def set_json(self, key: str, value: Any, ttl_seconds: int) -> None:
        await self.client.set(
            key,
            json.dumps(value, default=self._json_default),
            ex=ttl_seconds,
        )

    @staticmethod
    def _json_default(value: Any) -> str:
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")

    async def set_if_absent(self, key: str, value: str, ttl_seconds: int) -> bool:
        return bool(await self.client.set(key, value, ex=ttl_seconds, nx=True))

    async def delete(self, key: str) -> None:
        await self.client.delete(key)
