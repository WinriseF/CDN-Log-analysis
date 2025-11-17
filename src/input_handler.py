import gzip
import logging
from pathlib import Path
from typing import Iterator
from src.config import AppConfig
from src.clients.huawei_cdn_client import HuaweiCdnApiClient

def get_log_files(path: str, pattern: str) -> list[Path]:
    """获取指定路径下匹配模式的所有文件"""
    p = Path(path)
    if not p.is_dir():
        return []
    return list(p.glob(pattern))

def read_log_lines(file_path: Path) -> Iterator[str]:
    """逐行读取日志文件，支持 .gz 解压"""
    open_func = gzip.open if file_path.suffix == '.gz' else open
    try:
        # 使用 'rt' 模式以文本方式读取
        with open_func(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
            for line in f:
                yield line
    except FileNotFoundError:
        logging.error(f"文件未找到: {file_path}")
    except Exception as e:
        logging.error(f"读取文件时发生错误 {file_path}: {e}")

class InputHandler:
    def __init__(self, config: AppConfig):
        self.config = config

    def get_lines(self) -> Iterator[str]:
        """根据配置的 source_type 获取所有日志行"""
        source_type = self.config.input.source_type
        
        if source_type == 'local':
            # --- 本地文件模式 ---
            logging.info(f"使用 'local' 模式从路径 '{self.config.input.path}' 读取日志。")
            log_files = get_log_files(self.config.input.path, self.config.input.file_pattern)
            if not log_files:
                logging.warning(f"在 '{self.config.input.path}' 未找到匹配 '{self.config.input.file_pattern}' 的日志文件。")
                return iter([])

            logging.info(f"找到 {len(log_files)} 个日志文件进行处理。")
            for file in log_files:
                logging.info(f"--> 正在读取: {file.name}")
                yield from read_log_lines(file)
                
        elif source_type == 'api':
            # --- API 模式 ---
            logging.info(f"使用 'api' 模式从华为CDN API拉取日志。")
            if not self.config.input.api:
                logging.error("配置错误: source_type 为 'api'，但 'api' 配置块缺失。")
                return iter([])
            
            client = HuaweiCdnApiClient(self.config.input.api)
            log_urls = client.get_log_download_links()
            
            if not log_urls:
                logging.warning("API 未返回任何有效的日志文件链接。")
                return iter([])

            logging.info(f"从 API 获取到 {len(log_urls)} 个日志文件，开始下载和处理...")
            for url in log_urls:
                # 从URL中提取文件名用于日志记录
                file_name = url.split('?')[0].split('/')[-1]
                logging.info(f"--> 正在流式处理: {file_name}")
                yield from client.stream_log_file(url)

        else:
            logging.error(f"不支持的 source_type: '{source_type}'。请选择 'local' 或 'api'。")
            return iter([])