"""FastAPI 应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import leaderboard, summoner
from app.config import get_settings
from app.core.exceptions import (
    APIError,
    ConfigError,
    NetworkError,
    RateLimitError,
    ServerMaintenanceError,
    SummonerNotFoundError,
    TrackerException,
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="英雄联盟战绩查询 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 异常处理
@app.exception_handler(TrackerException)
async def tracker_exception_handler(request, exc: TrackerException):
    return JSONResponse(
        status_code=400,
        content={"success": False, "error": exc.code, "message": exc.message, "detail": exc.detail},
    )


@app.exception_handler(RateLimitError)
async def rate_limit_handler(request, exc: RateLimitError):
    return JSONResponse(
        status_code=429,
        content={"success": False, "error": exc.code, "message": exc.message},
    )


@app.exception_handler(SummonerNotFoundError)
async def not_found_handler(request, exc: SummonerNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": exc.code, "message": exc.message},
    )


@app.exception_handler(ServerMaintenanceError)
async def maintenance_handler(request, exc: ServerMaintenanceError):
    return JSONResponse(
        status_code=503,
        content={"success": False, "error": exc.code, "message": exc.message},
    )


@app.exception_handler(NetworkError)
async def network_handler(request, exc: NetworkError):
    return JSONResponse(
        status_code=503,
        content={"success": False, "error": exc.code, "message": exc.message},
    )


# 路由
app.include_router(summoner.router)
app.include_router(leaderboard.router)


# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name, "debug": settings.debug}


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "docs": "/docs",
        "health": "/health",
        "api_prefix": "/api",
    }


# 关闭时清理
@app.on_event("shutdown")
async def shutdown_event():
    from app.core.riot_client import riot
    from app.core.opgg_client import opgg
    await riot.close()
    await opgg.close()
