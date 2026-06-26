"""自定义异常类"""


class TrackerException(Exception):
    """基础异常"""
    def __init__(self, code: str, message: str, detail: str = ""):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class SummonerNotFoundError(TrackerException):
    def __init__(self, name: str):
        super().__init__(
            code="SUMMONER_NOT_FOUND",
            message=f"未找到召唤师「{name}」，请检查昵称和服务器",
        )


class APIError(TrackerException):
    def __init__(self, code: str, message: str, detail: str = ""):
        super().__init__(code=code, message=message, detail=detail)


class RateLimitError(APIError):
    def __init__(self):
        super().__init__(
            code="RATE_LIMITED",
            message="请求过于频繁，请稍后重试",
            detail="Riot API 每秒最多 20 次请求",
        )


class ServerMaintenanceError(APIError):
    def __init__(self):
        super().__init__(
            code="SERVER_MAINTENANCE",
            message="服务器维护中，请稍后再试",
        )


class NetworkError(TrackerException):
    def __init__(self):
        super().__init__(
            code="NETWORK_ERROR",
            message="网络异常，请检查网络连接",
        )


class ConfigError(TrackerException):
    def __init__(self, detail: str):
        super().__init__(
            code="CONFIG_ERROR",
            message="配置错误",
            detail=detail,
        )
