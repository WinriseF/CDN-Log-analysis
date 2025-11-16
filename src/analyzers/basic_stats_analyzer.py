# src/analyzers/basic_stats_analyzer.py
import pandas as pd
from src.config import AppConfig
from src.analyzers.base import BaseAnalyzer

class BasicStatsAnalyzer(BaseAnalyzer):
    """
    执行基础的统计分析，包括:
    - 状态码统计
    - Top N IP 及其 2xx 成功率
    - 每小时访问量
    """
    @property
    def name(self) -> str:
        return "basic_stats"

    def run(self, df: pd.DataFrame) -> dict:
        # --- 准备工作：确保数据类型正确 ---
        # 转换时间列，并设置为索引以便于按时间统计
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_convert('Asia/Shanghai')

        # 状态码统计
        status_counts = df['status_code'].value_counts().sort_index()

        # --- Top N IP ---
        top_n = self.config.analysis.top_n_count
        top_ips = df['client_ip'].value_counts().head(top_n)

        # --- Top N IP 2xx 成功率 ---
        top_ip_status_list = []
        for ip, total_count in top_ips.items():
            ip_df = df[df['client_ip'] == ip]
            count_2xx = ip_df[ip_df['status_code'].between(200, 299)].shape[0]
            ratio = round(count_2xx / total_count * 100, 2) if total_count > 0 else 0
            top_ip_status_list.append({
                'ip': str(ip), 
                'total_requests': total_count, 
                '2xx_requests': count_2xx, 
                '2xx_ratio(%)': ratio
            })
        top_ip_status_df = pd.DataFrame(top_ip_status_list)

        # --- 每小时访问量 ---
        hourly_counts = df.set_index('timestamp').resample('h').size()

        # --- 返回所有结果 ---
        return {
            "raw_logs_sample": df.head(100), # 提供一个原始日志样本供报告使用
            "status_counts": status_counts,
            "top_ips": top_ips,
            "top_ip_status": top_ip_status_df,
            "hourly_counts": hourly_counts
        }