from datetime import datetime
from pydantic import BaseModel, IPvAnyAddress

class LogEntry(BaseModel):
    """代表一条被解析后的日志行"""
    timestamp: datetime
    client_ip: IPvAnyAddress
    response_time_ms: int
    status_code: int
    response_size_bytes: int
    method: str
    domain: str
    path: str
    protocol: str
    user_agent: str
    referer: str | None = None
    cache_hit_status: str | None = None