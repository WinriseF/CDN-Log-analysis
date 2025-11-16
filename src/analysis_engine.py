import logging
import pandas as pd
from src.config import AppConfig
from src.analyzers.basic_stats_analyzer import BasicStatsAnalyzer 

class AnalysisEngine:
    def __init__(self, df: pd.DataFrame, config: AppConfig):
        self.df = df
        self.config = config
        self.results = {}
        
        # 在这里注册所有可用的分析器。
        self.available_analyzers = {
            "basic_stats": BasicStatsAnalyzer(config)
        }

    def run(self):
        """根据配置，运行所有启用的分析模块"""
        enabled_modules = self.config.analysis.modules
        logging.info(f"将要执行的分析模块: {enabled_modules}")

        for module_name in enabled_modules:
            analyzer = self.available_analyzers.get(module_name)
            if analyzer:
                logging.info(f"正在运行分析器: {analyzer.name}...")
                self.results[analyzer.name] = analyzer.run(self.df)
            else:
                logging.warning(f"配置了未知的分析模块 '{module_name}'，已跳过。")
        
        logging.info("所有分析模块执行完毕。")
        return self.results