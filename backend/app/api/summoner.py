"""召唤师 API 路由"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.core.models import (
    ChampionStat,
    MatchInfo,
    MatchParticipant,
    RankInfo,
    SummonerInfo,
)
from app.core.riot_client import riot
from app.core.opgg_client import opgg

router = APIRouter(prefix="/api/summoner", tags=["summoner"])


@router.get("/search", response_model=dict)
async def search_summoner(name: str = Query(..., min_length=1, max_length=32)):
    """
    按昵称搜索召唤师

    - **name**: 召唤师昵称
    """
    try:
        data = await riot.get_summoner_by_name(name)
        return {
            "success": True,
            "data": {
                "puuid": data.get("puuid"),
                "summonerId": data.get("id"),
                "accountId": data.get("accountId"),
                "name": data.get("name"),
                "profileIconId": data.get("profileIconId"),
                "summonerLevel": data.get("summonerLevel"),
            },
        }
    except Exception as e:
        from app.core.exceptions import SummonerNotFoundError
        if isinstance(e, SummonerNotFoundError):
            return {"success": False, "error": e.code, "message": e.message}
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{puuid}/profile", response_model=dict)
async def get_summoner_profile(puuid: str):
    """
    获取召唤师完整档案（基本信息 + 排位信息）

    - **puuid**: 召唤师 PUUID
    """
    try:
        # 并行获取基本信息 + 排位信息
        summoner_data, league_data = await asyncio.gather(
            riot.get_summoner_by_puuid(puuid),
            riot.get_league_entries(puuid),
        )

        info = SummonerInfo(
            puuid=summoner_data.get("puuid", ""),
            summoner_id=summoner_data.get("id", ""),
            account_id=summoner_data.get("accountId", ""),
            name=summoner_data.get("name", ""),
            profile_icon_id=summoner_data.get("profileIconId", 0),
            revision_date=summoner_data.get("revisionDate", 0),
            summoner_level=summoner_data.get("summonerLevel", 0),
        )

        ranks: list[RankInfo] = []
        for entry in league_data:
            ranks.append(RankInfo(
                queue_type=entry.get("queueType", ""),
                tier=entry.get("tier", "UNRANKED"),
                rank=entry.get("rank", ""),
                league_points=entry.get("leaguePoints", 0),
                wins=entry.get("wins", 0),
                losses=entry.get("losses", 0),
                is_fresh_blood=entry.get("freshBlood", False),
                is_hot_streak=entry.get("hotStreak", False),
                is_inactive=entry.get("inactive", False),
                is_veteran=entry.get("veteran", False),
            ))

        # 获取 OP.GG 额外数据
        opgg_data = await opgg.get_summoner_profile(info.name)

        return {
            "success": True,
            "data": {
                "summoner": {
                    "name": info.name,
                    "level": info.summoner_level,
                    "profileIconId": info.profile_icon_id,
                    "profileIconUrl": info.profile_icon_url,
                },
                "ranks": [
                    {
                        "queueType": r.queue_type,
                        "tier": r.tier,
                        "rank": r.rank,
                        "leaguePoints": r.league_points,
                        "wins": r.wins,
                        "losses": r.losses,
                        "winRate": r.win_rate,
                        "isHotStreak": r.is_hot_streak,
                        "isFreshBlood": r.is_fresh_blood,
                        "isVeteran": r.is_veteran,
                        "isInactive": r.is_inactive,
                    }
                    for r in ranks
                ],
                "opgg": opgg_data,
            },
        }
    except Exception as e:
        from app.core.exceptions import SummonerNotFoundError
        if isinstance(e, SummonerNotFoundError):
            return {"success": False, "error": e.code, "message": e.message}
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{puuid}/matches", response_model=dict)
async def get_recent_matches(
    puuid: str,
    count: int = Query(20, ge=1, le=100),
    start: int = Query(0, ge=0),
):
    """
    获取召唤师最近对局

    - **puuid**: 召唤师 PUUID
    - **count**: 返回对局数量（1-100）
    - **start**: 起始偏移
    """
    try:
        match_ids = await riot.get_match_ids(puuid, count=count, start=start)
        if not match_ids:
            return {"success": True, "data": {"matches": [], "total": 0}}

        # 并发获取所有对局详情
        match_tasks = [riot.get_match(mid) for mid in match_ids]
        raw_matches = await asyncio.gather(*match_tasks, return_exceptions=True)

        summoner = await riot.get_summoner_by_puuid(puuid)
        summoner_name = summoner.get("name", "")

        matches: list[dict] = []
        for raw in raw_matches:
            if isinstance(raw, Exception):
                continue
            if not raw:
                continue

            info = _parse_match(raw, summoner_name)
            matches.append(info)

        return {"success": True, "data": {"matches": matches, "total": len(matches)}}
    except Exception as e:
        from app.core.exceptions import SummonerNotFoundError
        if isinstance(e, SummonerNotFoundError):
            return {"success": False, "error": e.code, "message": e.message}
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{puuid}/stats", response_model=dict)
async def get_summoner_stats(puuid: str, match_count: int = Query(20, ge=1, le=100)):
    """
    获取召唤师统计信息

    - **puuid**: 召唤师 PUUID
    - **match_count**: 统计最近 N 场
    """
    try:
        match_ids = await riot.get_match_ids(puuid, count=match_count)
        if not match_ids:
            return {"success": True, "data": {"stats": _empty_stats()}}

        match_tasks = [riot.get_match(mid) for mid in match_ids]
        raw_matches = await asyncio.gather(*match_tasks, return_exceptions=True)

        summoner = await riot.get_summoner_by_puuid(puuid)
        summoner_name = summoner.get("name", "")

        wins = 0
        losses = 0
        total_kills = 0
        total_deaths = 0
        total_assists = 0
        total_gold = 0
        mode_counter: dict[str, int] = {}
        champ_counter: dict[str, dict] = {}

        for raw in raw_matches:
            if not isinstance(raw, dict):
                continue
            info = _parse_match(raw, summoner_name)
            for p in info["participants"]:
                if p["summonerName"] == summoner_name:
                    wins += 1 if p["win"] else 0
                    losses += 0 if p["win"] else 1
                    total_kills += p["kills"]
                    total_deaths += p["deaths"]
                    total_assists += p["assists"]
                    total_gold += p.get("goldEarned", 0)
                    mode_counter[info["gameMode"]] = mode_counter.get(info["gameMode"], 0) + 1
                    cn = p.get("championName", "Unknown")
                    if cn not in champ_counter:
                        champ_counter[cn] = {"games": 0, "wins": 0, "kills": 0, "deaths": 0, "assists": 0}
                    champ_counter[cn]["games"] += 1
                    champ_counter[cn]["wins"] += 1 if p["win"] else 0
                    champ_counter[cn]["kills"] += p["kills"]
                    champ_counter[cn]["deaths"] += p["deaths"]
                    champ_counter[cn]["assists"] += p["assists"]

        total = wins + losses
        stats = {
            "totalGames": total,
            "wins": wins,
            "losses": losses,
            "winRate": round(wins / total * 100, 1) if total > 0 else 0.0,
            "avgKills": round(total_kills / total, 1) if total > 0 else 0.0,
            "avgDeaths": round(total_deaths / total, 1) if total > 0 else 0.0,
            "avgAssists": round(total_assists / total, 1) if total > 0 else 0.0,
            "avgKDA": round((total_kills + total_assists) / max(total_deaths, 1), 2) if total > 0 else 0.0,
            "avgGold": round(total_gold / total) if total > 0 else 0,
            "modeDistribution": [
                {"mode": k, "count": v} for k, v in sorted(mode_counter.items(), key=lambda x: -x[1])
            ],
            "topChampions": sorted(
                [
                    {
                        "name": cn,
                        "games": d["games"],
                        "winRate": round(d["wins"] / d["games"] * 100, 1),
                        "avgKDA": round((d["kills"] + d["assists"]) / max(d["deaths"], 1), 2),
                        "kills": d["kills"],
                        "deaths": d["deaths"],
                        "assists": d["assists"],
                    }
                    for cn, d in champ_counter.items()
                ],
                key=lambda x: -x["games"],
            )[:10],
        }

        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _parse_match(raw: dict, target_name: str) -> dict:
    """解析单场对局数据"""
    info = raw.get("info", {})
    participants = info.get("participants", [])
    target = None
    for p in participants:
        if p.get("summonerName") == target_name:
            target = p
            break

    winning_team = 0
    for p in participants:
        if p.get("win") and p.get("teamId"):
            winning_team = p["teamId"]
            break

    return {
        "matchId": raw.get("metadata", {}).get("matchId", ""),
        "gameCreation": info.get("gameCreation", 0),
        "gameDuration": info.get("gameDuration", 0),
        "gameMode": info.get("gameMode", ""),
        "gameType": info.get("gameType", ""),
        "winningTeam": winning_team,
        "participants": [
            {
                "puuid": p.get("puuid", ""),
                "summonerName": p.get("summonerName", ""),
                "championId": p.get("championId", 0),
                "championName": p.get("championName", ""),
                "teamId": p.get("teamId", 0),
                "teamPosition": p.get("teamPosition", ""),
                "kills": p.get("kills", 0),
                "deaths": p.get("deaths", 0),
                "assists": p.get("assists", 0),
                "kda": _calc_kda(p.get("kills", 0), p.get("deaths", 0), p.get("assists", 0)),
                "champLevel": p.get("champLevel", 0),
                "goldEarned": p.get("goldEarned", 0),
                "totalDamageDealt": p.get("totalDamageDealtToChampions", 0),
                "totalDamageTaken": p.get("totalDamageTaken", 0),
                "win": p.get("win", False),
                "item0": p.get("item0", 0),
                "item1": p.get("item1", 0),
                "item2": p.get("item2", 0),
                "item3": p.get("item3", 0),
                "item4": p.get("item4", 0),
                "item5": p.get("item5", 0),
                "item6": p.get("item6", 0),
                "summoner1Id": p.get("summoner1Id", 0),
                "summoner2Id": p.get("summoner2Id", 0),
                "perkPrimaryStyle": p.get("perks", {}).get("styleSelections", [{}])[0].get("style", 0) if p.get("perks") else 0,
                "perkSubStyle": p.get("perks", {}).get("subStyle", 0) if p.get("perks") else 0,
                "lane": p.get("lane", ""),
                "role": p.get("role", ""),
            }
            for p in participants
        ],
    }


def _calc_kda(kills: int, deaths: int, assists: int) -> float:
    if deaths == 0:
        return round(kills + assists, 2)
    return round((kills + assists) / deaths, 2)


def _empty_stats() -> dict:
    return {
        "totalGames": 0,
        "wins": 0,
        "losses": 0,
        "winRate": 0.0,
        "avgKills": 0.0,
        "avgDeaths": 0.0,
        "avgAssists": 0.0,
        "avgKDA": 0.0,
        "avgGold": 0,
        "modeDistribution": [],
        "topChampions": [],
    }
