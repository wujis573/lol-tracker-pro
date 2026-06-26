"""OP.GG API 客户端"""
from __future__ import annotations

import asyncio
from typing import Any

import httpx

from app.config import get_settings
from app.core.cache import cache


class OpggClient:
    """OP.GG API 客户端"""

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.opgg_api_url
        self.api_key = self.settings.opgg_api_key
        self._http: httpx.AsyncClient | None = None

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None:
            headers = {"User-Agent": "LOL-Tracker/1.0"}
            if self.api_key:
                headers["x-api-key"] = self.api_key
            self._http = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers=headers,
            )
        return self._http

    async def get_summoner_profile(self, name: str) -> dict | None:
        """获取召唤师 OP.GG 资料"""
        cache_key = f"opgg:profile:{name}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached

        http = await self._get_http()
        try:
            resp = await http.get(
                f"{self.base_url}/api/summoner/name/{name}",
            )
            if resp.status_code == 200:
                data = resp.json()
                await cache.set(cache_key, data, ttl=300)
                return data
            return None
        except Exception:
            return None

    async def get_recent_matches(self, name: str) -> list[dict] | None:
        """获取最近对局（OP.GG）"""
        cache_key = f"opgg:matches:{name}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached

        http = await self._get_http()
        try:
            resp = await http.get(
                f"{self.base_url}/api/matches/recent",
                params={"summoner_name": name},
            )
            if resp.status_code == 200:
                data = resp.json()
                await cache.set(cache_key, data, ttl=120)
                return data
            return None
        except Exception:
            return None

    async def close(self):
        if self._http:
            await self._http.aclose()
            self._http = None


opgg = OpggClient()
