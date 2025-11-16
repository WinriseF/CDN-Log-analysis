# src/analyzers/geo_analyzer.py (最终修复和增强版)
import logging
import pandas as pd
import geoip2.database
from pathlib import Path
from src.config import AppConfig
from src.analyzers.base import BaseAnalyzer

class GeoAnalyzer(BaseAnalyzer):
    """
    分析IP地址的地理位置分布，并按请求数排序。
    """
    @property
    def name(self) -> str:
        return "geo_ip"

    def run(self, df: pd.DataFrame) -> dict:
        db_path_str = self.config.analysis.geoip_db_path
        if not db_path_str or not Path(db_path_str).exists():
            logging.warning(f"GeoIP 数据库文件未配置或不存在于 '{db_path_str}'，跳过地理位置分析。")
            return {}

        # --- 获取唯一的 IP 地址及其请求次数 ---
        # value_counts() 直接给出了 IP 和对应的次数，并且已按次数排序
        ip_counts = df['client_ip'].value_counts()
        
        # --- 为每个唯一 IP 查询地理位置 ---
        geo_data = []
        with geoip2.database.Reader(db_path_str) as reader:
            for ip_obj, count in ip_counts.items():
                ip_str = str(ip_obj) # 将 IP 对象转为字符串
                try:
                    response = reader.city(ip_str)
                    geo_data.append({
                        'ip': ip_str,
                        'count': count,
                        'country': response.country.name or 'Unknown',
                        'city': response.city.name or 'Unknown',
                    })
                except geoip2.errors.AddressNotFoundError:
                    geo_data.append({
                        'ip': ip_str,
                        'count': count,
                        'country': 'Unknown',
                        'city': 'Unknown',
                    })

        if not geo_data:
            return {}

        # --- 创建已排序的、带访问次数的 IP 地理位置详情 DataFrame ---
        ip_geo_details_df = pd.DataFrame(geo_data)

        # --- 计算各国/地区的总请求数 ---
        country_counts = ip_geo_details_df.groupby('country')['count'].sum().sort_values(ascending=False)

        return {
            "ip_geo_details": ip_geo_details_df.head(200), # 返回前200条IP详情
            "country_counts": country_counts.head(self.config.analysis.top_n_count)
        }