"""排行榜 API 路由"""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.core.riot_client import riot
from app.core.cache import cache

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("/challenger")
async def get_challenger_leaderboard(
    queue: str = Query("RANKED_SOLO_5x5", description="队列类型"),
    count: int = Query(20, ge=1, le=200),
):
    """
    获取最强王者排行榜

    - **queue**: 队列类型，默认 RANKED_SOLO_5x5
    - **count**: 返回数量（1-200）
    """
    try:
        cache_key = f"leaderboard:challenger:{queue}:{count}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return {"success": True, "data": cached}

        data = await riot._request(
            "GET",
            f"/lol/league/v4/challengerleagues/by-queue/{queue}",
            use_cache=True,
            cache_ttl=300,
        )

        if not data:
            return {"success": True, "data": []}

        entries = data.get("entries", [])
        result = sorted(entries, key=lambda x: x.get("leaguePoints", 0), reverse=True)[:count]
        leaderboard = [
            {
                "rank": i + 1,
                "puuid": e.get("puuid", ""),
                "summonerName": e.get("summonerName", ""),
                "tier": e.get("tier", "CHALLENGER"),
                "rankNum": e.get("rank", "I"),
                "leaguePoints": e.get("leaguePoints", 0),
                "wins": e.get("wins", 0),
                "losses": e.get("losses", 0),
                "winRate": round(e.get("wins", 0) / max(e.get("wins", 0) + e.get("losses", 0), 1) * 100, 1),
            }
            for i, e in enumerate(result)
        ]

        await cache.set(cache_key, leaderboard, ttl=300)
        return {"success": True, "data": leaderboard}
    except Exception as e:
        return {"success": False, "error": "LEADERBOARD_ERROR", "message": str(e)}


@router.get("/grandmaster")
async def get_grandmaster_leaderboard(
    queue: str = Query("RANKED_SOLO_5x5", description="队列类型"),
    count: int = Query(20, ge=1, le=200),
):
    """获取傲世宗师排行榜"""
    try:
        cache_key = f"leaderboard:grandmaster:{queue}:{count}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return {"success": True, "data": cached}

        data = await riot._request(
            "GET",
            f"/lol/league/v4/grandmasterleagues/by-queue/{queue}",
            use_cache=True,
            cache_ttl=300,
        )
        entries = data.get("entries", []) if data else []
        result = sorted(entries, key=lambda x: x.get("leaguePoints", 0), reverse=True)[:count]
        leaderboard = [
            {
                "rank": i + 1,
                "puuid": e.get("puuid", ""),
                "summonerName": e.get("summonerName", ""),
                "tier": e.get("tier", "GRANDMASTER"),
                "rankNum": e.get("rank", "I"),
                "leaguePoints": e.get("leaguePoints", 0),
                "wins": e.get("wins", 0),
                "losses": e.get("losses", 0),
                "winRate": round(e.get("wins", 0) / max(e.get("wins", 0) + e.get("losses", 0), 1) * 100, 1),
            }
            for i, e in enumerate(result)
        ]

        await cache.set(cache_key, leaderboard, ttl=300)
        return {"success": True, "data": leaderboard}
    except Exception as e:
        return {"success": False, "error": "LEADERBOARD_ERROR", "message": str(e)}
