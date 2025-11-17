import gzip
import logging
from pathlib import Path
from typing import Iterator
from src.config import AppConfig
from src.clients.huawei_cdn_client import HuaweiCdnApiClient

def get_log_files(path: str, pattern: str) -> list[Path]:
    """获取指定路径下匹配模式的所有文件"""
    # 确保路径存在，否则返回空列表
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
                return iter([])

            logging.info(f"找到 {len(log_files)} 个日志文件进行处理。")
            for file in log_files:
                logging.info(f"--> 正在读取: {file.name}")
                yield from read_log_lines(file)
                
        elif source_type == 'api':
            # --- API 模式的逻辑 ---
            logging.info(f"使用 'api' 模式从华为CDN API拉取日志。")
            if not self.config.input.api:
                logging.error("配置错误: source_type 为 'api'，但 'api' 配置块缺失。")
                return iter([])

            api_config = self.config.input.api
            client = HuaweiCdnApiClient(api_config)
            
            # 从API获取所有日志链接
            log_urls = client.get_log_download_links()
            if not log_urls:
                logging.warning("API 未返回任何有效的日志文件链接。")
                return iter([])
            
            logging.info(f"从 API 获取到 {len(log_urls)} 个日志文件的元数据。")

            # 如果开启了去重，则进行过滤
            urls_to_process = []
            if api_config.skip_existing_logs:
                # 获取本地缓存目录中已存在的文件名
                local_log_path = self.config.input.path or './logs/'
                existing_files = {f.name for f in get_log_files(local_log_path, self.config.input.file_pattern)}
                logging.info(f"在本地缓存目录 '{local_log_path}' 找到 {len(existing_files)} 个已存在的日志文件。")

                for url in log_urls:
                    file_name = url.split('?')[0].split('/')[-1]
                    if file_name in existing_files:
                        continue # 跳过已存在的文件
                    urls_to_process.append(url)
                
                logging.info(f"过滤后，有 {len(urls_to_process)} 个新日志文件需要处理。")
            else:
                urls_to_process = log_urls

            if not urls_to_process:
                logging.info("没有新的日志文件需要处理，程序结束。")
                return iter([])
            
            # 处理需要处理的日志
            for url in urls_to_process:
                file_name = url.split('?')[0].split('/')[-1]
                logging.info(f"--> 正在处理新日志: {file_name}")

                download_target_path = None
                if api_config.download_new_logs:
                    local_log_path = self.config.input.path or './logs/'
                    download_target_path = Path(local_log_path) / file_name

                # 调用新的下载与流式处理方法
                yield from client.download_and_stream_log_file(url, download_target_path)

        else:
            logging.error(f"不支持的 source_type: '{source_type}'。请选择 'local' 或 'api'。")
            return iter([])