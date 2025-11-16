import re
import logging
from typing import Optional
from datetime import datetime
from src.data_models import LogEntry
from src.config import AppConfig

# 匹配提供的格式
HUAWEI_CDN_PATTERN = re.compile(
    r'\[(?P<time_str>.*?)\]\s+'
    r'(?P<client_ip>\S+)\s+'
    r'(?P<response_time_ms>\d+)\s+'
    r'"(?P<referer>.*?)"\s+'
    r'"(?P<protocol>.*?)"\s+'
    r'"(?P<method>.*?)"\s+'
    r'"(?P<domain>.*?)"\s+'
    r'"(?P<path>.*?)"\s+'
    r'(?P<status_code>\d+)\s+'
    r'(?P<response_size_bytes>\d+)\s+'
    r'(?P<cache_hit_status>\S+)\s+'
    r'"(?P<user_agent>.*?)"\s+'
    r'".*?"\s+'  # other 字段，暂时忽略
    r'\S+'      # source_ip 字段，暂时忽略
)

class LogParser:
    def __init__(self, config: AppConfig):
        self.config = config
        # 未来可以根据 config.parser.format 选择不同的 pattern
        self.pattern = HUAWEI_CDN_PATTERN
        self.time_format = config.parser.time_format

    def parse_line(self, line: str) -> Optional[LogEntry]:
        match = self.pattern.match(line)
        if not match:
            return None

        data = match.groupdict()
        try:
            # 数据清洗和类型转换
            timestamp = datetime.strptime(data['time_str'], self.time_format)
            
            return LogEntry(
                timestamp=timestamp,
                client_ip=data['client_ip'],
                response_time_ms=int(data['response_time_ms']),
                referer=data['referer'] if data['referer'] != '-' else None,
                protocol=data['protocol'],
                method=data['method'],
                domain=data['domain'],
                path=data['path'],
                status_code=int(data['status_code']),
                response_size_bytes=int(data['response_size_bytes']),
                cache_hit_status=data['cache_hit_status'],
                user_agent=data['user_agent'],
            )
        except (ValueError, KeyError) as e:
            logging.warning(f"解析日志行失败: {line.strip()}. 错误: {e}")
            return None