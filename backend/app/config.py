"""配置管理 - 使用环境变量"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 应用
    app_name: str = "LOL Tracker"
    debug: bool = False

    # 国服 Riot API (通过 riot-gateway.cn)
    riot_gateway_url: str = "https://api.riot-gateway.cn"
    riot_api_key: str = ""

    # OP.GG API
    opgg_api_url: str = "https://api.op.gg"
    opgg_api_key: str = ""

    # 缓存
    redis_url: str = ""
    cache_ttl: int = 300  # 5分钟

    # 限流
    rate_limit_per_second: int = 20
    rate_limit_per_minute: int = 100

    # 区域
    default_platform: str = "cn"    # cn / kr / na1 / euw1 / jp1
    default_region: str = "asia"    # asia / americas / europe

    @property
    def has_riot_key(self) -> bool:
        return bool(self.riot_api_key)

    @property
    def has_opgg_key(self) -> bool:
        return bool(self.opgg_api_key)


def get_settings() -> Settings:
    return Settings()
