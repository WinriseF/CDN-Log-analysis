import gzip
import logging
from pathlib import Path
from typing import Iterator
from src.config import AppConfig

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
        self.config = config.input

    def get_lines(self) -> Iterator[str]:
        """获取所有日志文件的所有行"""
        log_files = get_log_files(self.config.path, self.config.file_pattern)
        if not log_files:
            logging.warning(f"在 '{self.config.path}' 未找到匹配 '{self.config.file_pattern}' 的日志文件。")
            return iter([]) # 返回一个空迭代器

        logging.info(f"找到 {len(log_files)} 个日志文件进行处理。")
        for file in log_files:
            logging.info(f"--> 正在读取: {file.name}")
            yield from read_log_lines(file)