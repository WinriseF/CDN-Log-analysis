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
            logging.info(f"使用 'local' 模式从路径 '{self.config.input.path}' 读取日志。")
            log_files = get_log_files(self.config.input.path, self.config.input.file_pattern)
            if not log_files:
                logging.warning(f"在 '{self.config.input.path}' 未找到匹配 '{self.config.input.file_pattern}' 的日志文件。")
                return
            logging.info(f"找到 {len(log_files)} 个日志文件进行处理。")
            for file in log_files:
                logging.info(f"--> 正在读取: {file.name}")
                yield from read_log_lines(file)
                
        elif source_type == 'api':
            # --- API 模式的全新的逻辑 ---
            logging.info(f"使用 'api' 模式从华为CDN API拉取日志。")
            if not self.config.input.api:
                logging.error("配置错误: source_type 为 'api'，但 'api' 配置块缺失。")
                return

            api_config = self.config.input.api
            client = HuaweiCdnApiClient(api_config)
            
            # 从API获取目标任务全集
            log_urls = client.get_log_download_links()
            if not log_urls:
                logging.warning("API 未返回任何有效的日志文件链接，分析结束。")
                return
            
            logging.info(f"API返回了 {len(log_urls)} 个目标日志文件。")

            # 准备本地缓存信息
            local_log_path_str = self.config.input.path or './logs/'
            local_log_path = Path(local_log_path_str)
            existing_files = {f.name for f in get_log_files(local_log_path_str, self.config.input.file_pattern)}
            logging.info(f"在本地缓存目录 '{local_log_path_str}' 找到 {len(existing_files)} 个日志文件。")

            # 遍历目标任务全集，决定是从本地读还是从云端下载
            for url in log_urls:
                file_name = url.split('?')[0].split('/')[-1]
                local_file = local_log_path / file_name

                # 决定是否使用本地缓存
                use_local_cache = api_config.skip_existing_logs and file_name in existing_files

                if use_local_cache:
                    # 如果使用本地缓存，直接从本地读取
                    logging.info(f"--> 正在从本地缓存读取: {file_name}")
                    yield from read_log_lines(local_file)
                else:
                    # 否则，从云端下载并处理
                    logging.info(f"--> 正在从云端下载并处理: {file_name}")
                    download_target_path = local_file if api_config.download_new_logs else None
                    yield from client.download_and_stream_log_file(url, download_target_path)

        else:
            logging.error(f"不支持的 source_type: '{source_type}'。请选择 'local' 或 'api'。")
            return