# src/analyzers/base.py
from abc import ABC, abstractmethod
import pandas as pd
from src.config import AppConfig

class BaseAnalyzer(ABC):
    """所有分析器模块的抽象基类"""
    def __init__(self, config: AppConfig):
        self.config = config

    @property
    @abstractmethod
    def name(self) -> str:
        """为分析器提供一个唯一的名称, 例如 'basic_stats'"""
        pass

    @abstractmethod
    def run(self, df: pd.DataFrame) -> dict:
        """执行分析并返回一个包含结果的字典"""
        pass