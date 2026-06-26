"""Riot API 客户端 - 国服代理"""
from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from app.config import get_settings
from app.core.exceptions import (
    NetworkError,
    RateLimitError,
    ServerMaintenanceError,
    SummonerNotFoundError,
)
from app.core.cache import cache


class RateLimiter:
    """令牌桶限流器"""

    def __init__(self, per_second: int = 20, per_minute: int = 100):
        self.per_second = per_second
        self.per_minute = per_minute
        self._second_tokens = per_second
        self._minute_tokens = per_minute
        self._last_second = time.monotonic()
        self._last_minute = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            # 每秒重置
            if now - self._last_second >= 1.0:
                self._second_tokens = self.per_second
                self._last_second = now
            # 每分钟重置
            if now - self._last_minute >= 60.0:
                self._minute_tokens = self.per_minute
                self._last_minute = now

            # 检查限制
            if self._second_tokens <= 0 or self._minute_tokens <= 0:
                wait_time = 1.0 if self._second_tokens <= 0 else 60.0
                await asyncio.sleep(wait_time)
                return await self.acquire()

            self._second_tokens -= 1
            self._minute_tokens -= 1


class RiotClient:
    """Riot API 客户端（国服 via riot-gateway.cn）"""

    # DDragon 版本缓存
    _ddragon_version: str | None = None

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.riot_gateway_url
        self.api_key = self.settings.riot_api_key
        self.limiter = RateLimiter(
            per_second=self.settings.rate_limit_per_second,
            per_minute=self.settings.rate_limit_per_minute,
        )
        self._http: httpx.AsyncClient | None = None

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers={
                    "User-Agent": "LOL-Tracker/1.0",
                    "Accept": "application/json",
                },
            )
        return self._http

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        use_cache: bool = True,
        cache_ttl: int = 300,
    ) -> Any:
        """发起请求（含限流、重试、缓存）"""
        await self.limiter.acquire()

        cache_key = f"riot:{method}:{path}:{params}"
        if use_cache:
            cached = await cache.get(cache_key)
            if cached is not None:
                return cached

        http = await self._get_http()
        url = f"{self.base_url}{path}"

        last_error: Exception | None = None
        for attempt in range(3):
            try:
                resp = await http.request(method, url, params=params)
                if resp.status_code == 404:
                    raise SummonerNotFoundError(params.get("name", "unknown") if params else "unknown")
                if resp.status_code == 429:
                    raise RateLimitError()
                if resp.status_code in (502, 503, 504):
                    last_error = ServerMaintenanceError()
                    await asyncio.sleep(2 ** attempt)
                    continue
                if resp.status_code >= 400:
                    last_error = NetworkError()
                    await asyncio.sleep(1)
                    continue
                data = resp.json()
                if use_cache:
                    await cache.set(cache_key, data, ttl=cache_ttl)
                return data
            except httpx.HTTPError as e:
                last_error = NetworkError()
                await asyncio.sleep(2 ** attempt)

        raise last_error or NetworkError()

    async def close(self):
        if self._http:
            await self._http.aclose()
            self._http = None

    # ── 召唤师 ──

    async def get_summoner_by_name(self, name: str) -> dict:
        """按昵称获取召唤师信息"""
        return await self._request(
            "GET", "/lol/summoner/v4/summoners/by-name/{name}",
            params={"name": name},
            use_cache=True,
            cache_ttl=300,
        )

    async def get_summoner_by_puuid(self, puuid: str) -> dict:
        """按 PUUID 获取召唤师信息"""
        return await self._request(
            "GET", "/lol/summoner/v4/summoners/by-puuid/{puuid}",
            params={"puuid": puuid},
            use_cache=True,
            cache_ttl=300,
        )

    # ── 排位 ──

    async def get_league_entries(self, summoner_id: str) -> list[dict]:
        """获取排位信息"""
        return await self._request(
            "GET", "/lol/league/v4/entries/by-summoner/{summonerId}",
            params={"summonerId": summoner_id},
            use_cache=True,
            cache_ttl=120,
        ) or []

    # ── 对局 ──

    async def get_match_ids(self, puuid: str, count: int = 20, start: int = 0) -> list[str]:
        """获取对局 ID 列表"""
        return await self._request(
            "GET", "/lol/match/v5/matches/by-puuid/{puuid}/ids",
            params={"puuid": puuid, "count": count, "start": start},
            use_cache=True,
            cache_ttl=60,
        ) or []

    async def get_match(self, match_id: str) -> dict:
        """获取对局详情"""
        return await self._request(
            "GET", "/lol/match/v5/matches/{matchId}",
            params={"matchId": match_id},
            use_cache=True,
            cache_ttl=3600,
        )

    # ── DDragon 静态数据 ──

    @classmethod
    async def get_ddragon_version(cls) -> str:
        if cls._ddragon_version is None:
            async with httpx.AsyncClient() as http:
                resp = await http.get("https://ddragon.leagueoflegends.com/api/versions.json")
                versions = resp.json()
                cls._ddragon_version = versions[0]
        return cls._ddragon_version

    @classmethod
    def get_champion_icon_url(cls, champion_id: int) -> str:
        import asyncio
        try:
            version = asyncio.run(cls.get_ddragon_version())
        except Exception:
            version = "14.10.1"
        return f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{champion_id}.png"

    @staticmethod
    def get_item_icon_url(item_id: int) -> str:
        return f"https://ddragon.leagueoflegends.com/cdn/14.10.1/img/item/{item_id}.png"

    @staticmethod
    def get_summoner_spell_url(spell_id: int) -> str:
        return f"https://ddragon.leagueoflegends.com/cdn/14.10.1/img/spell/{spell_id}.png"


# 全局单例
riot = RiotClient()
