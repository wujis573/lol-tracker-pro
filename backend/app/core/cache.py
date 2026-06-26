"""Redis 缓存层"""
from __future__ import annotations

import json
import hashlib
from typing import Any, Optional

from app.config import get_settings


class Cache:
    """缓存封装，无 Redis 时退化为内存缓存"""

    def __init__(self):
        self.settings = get_settings()
        self._redis = None
        self._memory: dict[str, str] = {}

    async def _get_redis(self):
        if self._redis is not None:
            return self._redis
        if self.settings.redis_url:
            try:
                import redis.asyncio as aioredis
                self._redis = aioredis.from_url(
                    self.settings.redis_url,
                    decode_responses=True,
                )
                return self._redis
            except ImportError:
                pass
        return None

    def _make_key(self, prefix: str, *args: str) -> str:
        raw = f"{prefix}:{':'.join(args)}"
        return f"lol:tracker:{hashlib.md5(raw.encode()).hexdigest()}"

    async def get(self, key: str) -> Optional[Any]:
        redis = await self._get_redis()
        if redis:
            val = await redis.get(key)
            if val:
                return json.loads(val)
            return None
        # 内存缓存
        raw = self._memory.get(key)
        return json.loads(raw) if raw else None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        data = json.dumps(value, ensure_ascii=False)
        redis = await self._get_redis()
        if redis:
            await redis.setex(key, ttl, data)
            return
        self._memory[key] = data

    async def delete(self, key: str) -> None:
        redis = await self._get_redis()
        if redis:
            await redis.delete(key)
            return
        self._memory.pop(key, None)

    async def exists(self, key: str) -> bool:
        redis = await self._get_redis()
        if redis:
            return bool(await redis.exists(key))
        return key in self._memory


# 全局单例
cache = Cache()
