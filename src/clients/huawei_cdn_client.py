import gzip
import logging
import requests
from typing import Iterator
from pathlib import Path
from datetime import datetime, timezone

from huaweicloudsdkcore.auth.credentials import GlobalCredentials
from huaweicloudsdkcdn.v1 import CdnClient, ShowLogsRequest

from src.config import InputApiConfig


class HuaweiCdnApiClient:
    def __init__(self, config: InputApiConfig):
        credentials = GlobalCredentials(
            ak=config.access_key,
            sk=config.secret_key.get_secret_value()
        )
        self.client = CdnClient.new_builder() \
            .with_credentials(credentials) \
            .with_endpoint(config.endpoint) \
            .build()
        self.config = config

    def get_log_download_links(self) -> list[str]:
        """
        [SDK版本] 获取指定时间范围内的所有日志下载链接。
        """
        try:
            # --- 将ISO格式的时间字符串转换为毫秒级Unix时间戳 ---
            try:
                start_dt = datetime.fromisoformat(self.config.start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(self.config.end_time.replace('Z', '+00:00'))
                
                # 转换为毫秒时间戳 (long number)
                start_time_ms = int(start_dt.timestamp() * 1000)
                end_time_ms = int(end_dt.timestamp() * 1000)

            except ValueError:
                logging.error("配置文件中的 start_time 或 end_time 格式无效。请使用 'YYYY-MM-DDTHH:MM:SSZ' 格式。")
                return []
            # -----------------------------------------------------------

            # 创建一个请求对象，使用转换后的时间戳
            request = ShowLogsRequest(
                domain_name=self.config.domain_name,
                start_time=start_time_ms,
                end_time=end_time_ms,
                page_size=1000
            )

            logging.info("正在通过华为云SDK请求日志链接...")
            
            # 调用SDK的接口方法
            response = self.client.show_logs(request)

            # 处理响应
            if hasattr(response, 'logs') and response.logs:
                logging.info(f"SDK成功获取到 {len(response.logs)} 个日志文件链接。")
                return [log.link for log in response.logs]
            else:
                logging.warning("SDK请求成功，但API未返回任何日志文件链接。")
                return []

        except Exception as e:
            logging.error(f"通过华为云SDK获取日志链接失败: {e}", exc_info=True)
            return []

    def download_and_stream_log_file(self, url: str, download_path: Path | None = None) -> Iterator[str]:
        try:
            with requests.get(url, stream=True, timeout=180) as r:
                r.raise_for_status()
                if download_path:
                    download_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(download_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    logging.info(f"日志已成功下载到: {download_path}")
                    from src.input_handler import read_log_lines
                    yield from read_log_lines(download_path)
                else:
                    with gzip.open(r.raw, 'rt', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            yield line
        except requests.exceptions.RequestException as e:
            logging.error(f"下载日志文件失败 {url}: {e}")
        except Exception as e:
            logging.error(f"处理流式日志文件时出错 {url}: {e}")