import gzip
import logging
import requests
import datetime
import hashlib
import hmac
from typing import Iterator
from urllib.parse import urlencode

from src.config import InputApiConfig

# 华为云API签名常量
ALGORITHM = "SDK-HMAC-SHA256"
HEADER_X_SDK_DATE = "X-Sdk-Date"
HEADER_HOST = "host"
SIGNED_HEADERS = f"{HEADER_HOST};{HEADER_X_SDK_DATE}"

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

class HuaweiCdnApiClient:
    def __init__(self, config: InputApiConfig):
        self.config = config

    def _get_signature(self, request: dict) -> str:
        """根据请求信息生成华为云API签名 (V3)"""
        # 使用 SK 对日期进行 HMAC-SHA256 加密
        signing_key = sign(("SDK" + self.config.secret_key.get_secret_value()).encode('utf-8'), request['t_stamp_short'])
        
        # 拼接规范请求字符串
        canonical_request = (
            f"{request['method']}\n"
            f"{request['canonical_uri']}\n"
            f"{request['canonical_querystring']}\n"
            f"{request['canonical_headers']}\n"
            f"{SIGNED_HEADERS}\n"
            f"{request['request_payload']}"
        )
        
        # 对规范请求进行 SHA256 Hash
        hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        
        # 拼接待签名字符串
        string_to_sign = (
            f"{ALGORITHM}\n"
            f"{request['t_stamp_long']}\n"
            f"{hashed_canonical_request}"
        )
        
        # 使用派生密钥对待签名字符串进行 HMAC-SHA256 加密，得到签名
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    def get_log_download_links(self) -> list[str]:
        """获取指定时间范围内的所有日志下载链接"""
        t = datetime.datetime.utcnow()
        t_stamp_long = t.strftime('%Y%m%dT%H%M%SZ')
        t_stamp_short = t.strftime('%Y%m%d')
        
        params = {
            "domain_name": self.config.domain_name,
            "start_time": self.config.start_time,
            "end_time": self.config.end_time,
            "page_size": 1000  # 一次性尽可能多地获取
        }
        canonical_querystring = urlencode(params, safe=":")
        
        request_details = {
            'method': 'GET',
            'canonical_uri': '/v1.0/cdn/logs',
            'canonical_querystring': canonical_querystring,
            'canonical_headers': f"{HEADER_HOST}:{self.config.endpoint}\n{HEADER_X_SDK_DATE}:{t_stamp_long}\n",
            'request_payload': hashlib.sha256(b"").hexdigest(),
            't_stamp_long': t_stamp_long,
            't_stamp_short': t_stamp_short
        }

        signature = self._get_signature(request_details)

        headers = {
            'Content-Type': 'application/json;charset=utf8',
            'host': self.config.endpoint,
            'X-Sdk-Date': t_stamp_long,
            'Authorization': (
                f"{ALGORITHM} "
                f"Access={self.config.access_key}, "
                f"SignedHeaders={SIGNED_HEADERS}, "
                f"Signature={signature}"
            )
        }

        url = f"https://{self.config.endpoint}{request_details['canonical_uri']}?{canonical_querystring}"

        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('logs'):
                return []
            
            return [log['link'] for log in data['logs']]
            
        except requests.exceptions.RequestException as e:
            logging.error(f"请求华为CDN API获取日志链接失败: {e}")
            logging.error(f"API响应: {e.response.text if e.response else 'No Response'}")
            return []

    def stream_log_file(self, url: str) -> Iterator[str]:
        """从给定的URL流式下载并解压gz日志文件，逐行返回"""
        try:
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                # 使用 gzip.open 直接处理流式响应内容，无需先保存到磁盘
                with gzip.open(r.raw, 'rt', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        yield line
        except requests.exceptions.RequestException as e:
            logging.error(f"下载日志文件失败 {url}: {e}")
        except Exception as e:
            logging.error(f"处理流式日志文件时出错 {url}: {e}")