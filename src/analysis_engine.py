import logging
import pandas as pd
from typing import Dict
from src.config import AppConfig
from src.analyzers.base import BaseAnalyzer
from src.analyzers.basic_stats_analyzer import BasicStatsAnalyzer
from src.analyzers.geo_analyzer import GeoAnalyzer
from src.analyzers.api_geo_analyzer import ApiGeoAnalyzer

class AnalysisEngine:
    def __init__(self, df: pd.DataFrame, config: AppConfig):
        self.df = df
        self.config = config
        self.results = {}
        self.available_analyzers = self._load_analyzers()

    def _load_analyzers(self) -> Dict[str, BaseAnalyzer]:
        """根据配置动态加载分析器"""
        analyzers = {}
        
        # 始终加载基础统计模块
        if "basic_stats" in self.config.analysis.modules:
            analyzers["basic_stats"] = BasicStatsAnalyzer(self.config)

        # 根据 provider 智能选择地理位置分析器
        if "geo_ip" in self.config.analysis.modules:
            provider = self.config.analysis.geoip.provider
            if provider == 'api':
                logging.info("使用 API 地理位置分析器。")
                analyzers["geo_ip"] = ApiGeoAnalyzer(self.config)
            elif provider == 'local':
                logging.info("使用本地数据地理位置分析器。")
                analyzers["geo_ip"] = GeoAnalyzer(self.config)
            else:
                logging.warning(f"未知的 GeoIP provider: '{provider}'。跳过地理位置分析。")
        
        return analyzers

    def run(self):
        """运行所有已加载的分析模块"""
        for name, analyzer in self.available_analyzers.items():
            logging.info(f"正在运行分析器: {name}...")
            self.results[name] = analyzer.run(self.df)
        
        logging.info("所有分析模块执行完毕。")
        return self.results