import logging
import pandas as pd
import requests
from typing import List, Dict, Any
from src.config import AppConfig
from src.analyzers.base import BaseAnalyzer

class ApiGeoAnalyzer(BaseAnalyzer):
    """
    使用在线API分析IP地址的地理位置分布。
    """
    def __init__(self, config: AppConfig):
        super().__init__(config)
        self.api_config = self.config.analysis.geoip.api

    @property
    def name(self) -> str:
        return "geo_ip_api"

    def _query_batch(self, ip_batch: List[str]) -> List[Dict[str, Any]]:
        """发送单个批量查询请求"""
        try:
            response = requests.post(
                str(self.api_config.endpoint), # Pydantic v2 HttpUrl -> str
                json=ip_batch,
                timeout=self.api_config.timeout
            )
            response.raise_for_status()  # 如果请求失败 (如 4xx, 5xx), 则抛出异常
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"IP API 请求失败: {e}")
            return []

    def run(self, df: pd.DataFrame) -> dict:
        ip_counts = df['client_ip'].value_counts()
        unique_ips = [str(ip) for ip in ip_counts.index]
        geo_data = []

        # 将IP列表分块
        ip_chunks = [
            unique_ips[i:i + self.api_config.batch_size]
            for i in range(0, len(unique_ips), self.api_config.batch_size)
        ]
        
        logging.info(f"将向 API 发送 {len(ip_chunks)} 个批量请求...")

        for chunk in ip_chunks:
            api_results = self._query_batch(chunk)
            for result in api_results:
                if result.get('status') == 'success':
                    geo_data.append({
                        'ip': result.get('query'),
                        'country': result.get('country', 'Unknown'),
                        'city': result.get('city', 'Unknown'),
                        'isp': result.get('isp', 'Unknown') # <--- 新增获取ISP（运营商）
                    })

        if not geo_data:
            logging.warning("未能从 API 获取任何地理位置数据。")
            return {}

        geo_df = pd.DataFrame(geo_data)
        
        # 将 IP 访问次数合并到地理位置数据中
        ip_counts_df = ip_counts.reset_index()
        ip_counts_df.columns = ['ip_obj', 'count']
        ip_counts_df['ip'] = ip_counts_df['ip_obj'].astype(str)
        
        ip_geo_details_df = pd.merge(geo_df, ip_counts_df[['ip', 'count']], on='ip', how='left')
        ip_geo_details_df = ip_geo_details_df.sort_values(by='count', ascending=False).fillna('N/A')

        # 计算各国/地区的总请求数
        country_counts = ip_geo_details_df.groupby('country')['count'].sum().sort_values(ascending=False)

        return {
            "ip_geo_details": ip_geo_details_df.head(200),
            "country_counts": country_counts.head(self.config.analysis.top_n_count)
        }