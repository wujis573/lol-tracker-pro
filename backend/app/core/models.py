"""数据模型"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SummonerInfo:
    """召唤师基础信息"""
    puuid: str
    summoner_id: str
    account_id: str
    name: str
    profile_icon_id: int
    revision_date: int
    summoner_level: int

    @property
    def profile_icon_url(self) -> str:
        return f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{self.profile_icon_id}.png"


@dataclass
class RankInfo:
    """排位信息"""
    queue_type: str       # RANKED_SOLO_5x5 / RANKED_FLEX_SR
    tier: str             # IRON / BRONZE / SILVER / GOLD / PLATINUM / DIAMOND / MASTER / GRANDMASTER / CHALLENGER
    rank: str             # I / II / III / IV
    league_points: int
    wins: int
    losses: int
    is_fresh_blood: bool
    is_hot_streak: bool
    is_inactive: bool
    is_veteran: bool

    @property
    def win_rate(self) -> float:
        total = self.wins + self.losses
        return round(self.wins / total * 100, 1) if total > 0 else 0.0

    @property
    def tier_icon_url(self) -> str:
        rank_map = {
            "IRON": 0, "BRONZE": 1, "SILVER": 2, "GOLD": 3,
            "PLATINUM": 4, "DIAMOND": 5, "MASTER": 6,
            "GRANDMASTER": 7, "CHALLENGER": 8,
        }
        rank_num_map = {"I": 1, "II": 2, "III": 3, "IV": 4}
        tier_idx = rank_map.get(self.tier, 0)
        rank_idx = rank_num_map.get(self.rank, 1)
        if self.tier in ("MASTER", "GRANDMASTER", "CHALLENGER"):
            rank_idx = 1
        return f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/content/src/leagueclient/rankedcrests/emblem-cb-tier{tier_idx}_tier{rank_idx}.png"


@dataclass
class MatchParticipant:
    """对局参与者"""
    puuid: str
    summoner_name: str
    champion_id: int
    champion_name: str
    team_id: int
    team_position: str
    kills: int
    deaths: int
    assists: int
    kda: float = 0.0
    champ_level: int = 0
    gold_earned: int = 0
    total_damage_dealt: int = 0
    total_damage_taken: int = 0
    win: bool = False
    item0: int = 0
    item1: int = 0
    item2: int = 0
    item3: int = 0
    item4: int = 0
    item5: int = 0
    item6: int = 0
    summoner1_id: int = 0
    summoner2_id: int = 0
    perk_primary_style: int = 0
    perk_sub_style: int = 0
    lane: str = ""
    role: str = ""

    def __post_init__(self):
        if self.deaths > 0:
            self.kda = round((self.kills + self.assists) / self.deaths, 2)
        else:
            self.kda = round(self.kills + self.assists, 2)


@dataclass
class MatchInfo:
    """对局信息"""
    match_id: str
    game_creation: int
    game_duration: int
    game_mode: str
    game_type: str
    game_version: str
    participants: list[MatchParticipant] = field(default_factory=list)
    winning_team: int = 0

    @property
    def is_win(self) -> bool:
        return self.winning_team != 0

    @property
    def game_result(self) -> str:
        return "胜利" if self.is_win else "失败"

    @property
    def game_time_str(self) -> str:
        if self.game_duration < 3600:
            m, s = divmod(self.game_duration, 60)
            return f"{m}分{s}秒"
        h, rem = divmod(self.game_duration, 3600)
        m, s = divmod(rem, 60)
        return f"{h}小时{m}分{s}秒"

    @property
    def game_mode_cn(self) -> str:
        mode_map = {
            "CLASSIC": "经典模式",
            "ARAM": "极地大乱斗",
            "URF": "无限火力",
            "TFT": "云顶之弈",
            "ARURF": "无限乱斗",
            "CHERRY": "斗魂竞技场",
            "PRACTICETOOL": "训练模式",
            "TUTORIAL": "新手教程",
        }
        return mode_map.get(self.game_mode, self.game_mode)

    @property
    def champion_icon_url(self) -> str:
        return "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/{id}.png"

    @property
    def item_icon_url(self) -> str:
        return "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/item-icons/{id}.png"

    @property
    def spell_icon_url(self) -> str:
        return "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/summoner-spells/{id}.png"

    @property
    def rune_icon_url(self) -> str:
        return "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perk-images/styles/{style_id}/{icon_name}.png"


@dataclass
class ChampionStat:
    """英雄使用统计"""
    champion_id: int
    champion_name: str
    champion_title: str
    games: int
    wins: int
    losses: int
    kills: int
    deaths: int
    assists: int
    kda: float = 0.0

    def __post_init__(self):
        if self.deaths > 0:
            self.kda = round((self.kills + self.assists) / self.deaths, 2)
        else:
            self.kda = round(self.kills + self.assists, 2)

    @property
    def win_rate(self) -> float:
        total = self.wins + self.losses
        return round(self.wins / total * 100, 1) if total > 0 else 0.0

    @property
    def avg_kills(self) -> float:
        return round(self.kills / self.games, 1) if self.games > 0 else 0.0

    @property
    def avg_deaths(self) -> float:
        return round(self.deaths / self.games, 1) if self.games > 0 else 0.0

    @property
    def avg_assists(self) -> float:
        return round(self.assists / self.games, 1) if self.games > 0 else 0.0


@dataclass
class LeaderboardEntry:
    """排行榜条目"""
    rank: int
    puuid: str
    summoner_name: str
    tier: str
    rank_num: str
    league_points: int
    wins: int
    losses: int
