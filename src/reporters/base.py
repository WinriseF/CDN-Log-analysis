from abc import ABC, abstractmethod
from src.config import AppConfig

class BaseReporter(ABC):
    """所有报告器模块的抽象基类"""
    def __init__(self, results: dict, config: AppConfig):
        self.results = results
        self.config = config
    
    @abstractmethod
    def generate(self):
        """生成报告"""
        pass