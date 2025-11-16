# src/analyzers/geo_analyzer.py (已修正地区归属问题)
import logging
import pandas as pd
import geoip2.database
from pathlib import Path
from src.config import AppConfig
from src.analyzers.base import BaseAnalyzer

CHINA_REGIONS = {'Hong Kong', 'Taiwan', 'Macao'}

class GeoAnalyzer(BaseAnalyzer):
    """
    分析IP地址的地理位置分布，并按请求数排序。
    (包含地区归属修正逻辑)
    """
    @property
    def name(self) -> str:
        return "geo_ip"

    def run(self, df: pd.DataFrame) -> dict:
        db_path_str = self.config.analysis.geoip.local.db_path
        if not db_path_str or not Path(db_path_str).exists():
            logging.warning(f"GeoIP 数据库文件未配置或不存在于 '{db_path_str}'，跳过地理位置分析。")
            return {}

        ip_counts = df['client_ip'].value_counts()
        geo_data = []

        with geoip2.database.Reader(db_path_str) as reader:
            for ip_obj, count in ip_counts.items():
                ip_str = str(ip_obj)
                try:
                    response = reader.city(ip_str)
                    
                    country_name = response.country.name or 'Unknown'
                    if country_name in CHINA_REGIONS:
                        country_name = 'China'

                    geo_data.append({
                        'ip': ip_str,
                        'count': count,
                        'country': country_name, # 修正
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

        ip_geo_details_df = pd.DataFrame(geo_data)
        country_counts = ip_geo_details_df.groupby('country')['count'].sum().sort_values(ascending=False)

        return {
            "ip_geo_details": ip_geo_details_df.head(200),
            "country_counts": country_counts.head(self.config.analysis.top_n_count)
        }