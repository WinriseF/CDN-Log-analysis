import pandas as pd
from pathlib import Path
from datetime import datetime
from src.config import AppConfig
from src.reporters.base import BaseReporter

class ExcelReporter(BaseReporter):
    """将详细分析结果和图表输出到 Excel 文件"""
    def generate(self):
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(self.config.output.report_path) / f"cdn_report_{timestamp_str}.xlsx"

        if 'basic_stats' not in self.results:
            return

        stats = self.results['basic_stats']

        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            # --- 原始日志样本 ---
            # <-- 创建一个副本以避免修改原始数据
            df_raw_logs = stats['raw_logs_sample'].copy()
            # <-- 移除时间戳列的时区信息
            df_raw_logs['timestamp'] = df_raw_logs['timestamp'].dt.tz_localize(None)
            df_raw_logs.to_excel(writer, sheet_name='RawLogsSample', index=False)
            
            workbook = writer.book

            # --- 状态码分布 ---
            status_counts = stats['status_counts']
            status_counts.to_frame('count').to_excel(writer, sheet_name='StatusCounts')
            worksheet = writer.sheets['StatusCounts']
            chart1 = workbook.add_chart({'type': 'column'})
            chart1.add_series({
                'categories': ['StatusCounts', 1, 0, len(status_counts), 0],
                'values':     ['StatusCounts', 1, 1, len(status_counts), 1],
                'name': 'Status Code Count'
            })
            chart1.set_title({'name': 'Status Code Distribution'})
            worksheet.insert_chart('D2', chart1)

            # --- Top IP ---
            top_ips = stats['top_ips']
            top_ips.to_frame('count').to_excel(writer, sheet_name='TopIPs')
            worksheet = writer.sheets['TopIPs']
            chart2 = workbook.add_chart({'type': 'bar'})
            chart2.add_series({
                'categories': ['TopIPs', 1, 0, len(top_ips), 0],
                'values':     ['TopIPs', 1, 1, len(top_ips), 1],
                'name': 'Top IPs'
            })
            chart2.set_title({'name': f'Top {self.config.analysis.top_n_count} IPs'})
            worksheet.insert_chart('D2', chart2)

            # --- Top IP 2XX 占比 ---
            top_ip_status_df = stats['top_ip_status']
            top_ip_status_df.to_excel(writer, sheet_name='TopIP_2XX', index=False)
            worksheet = writer.sheets['TopIP_2XX']
            chart3 = workbook.add_chart({'type': 'column'})
            chart3.add_series({
                'categories': ['TopIP_2XX', 1, 0, len(top_ip_status_df), 0],
                'values':     ['TopIP_2XX', 1, 3, len(top_ip_status_df), 3],
                'name': '2XX Ratio'
            })
            chart3.set_title({'name': 'Top IP 2XX Ratio (%)'})
            worksheet.insert_chart('E2', chart3)

            # --- 按小时访问量 ---
            # <-- 创建一个副本
            df_hourly = stats['hourly_counts'].copy()
            # <-- 移除时间索引的时区信息
            df_hourly.index = df_hourly.index.tz_localize(None)
            df_hourly.to_frame('count').to_excel(writer, sheet_name='HourlyCounts')
            worksheet = writer.sheets['HourlyCounts']
            chart4 = workbook.add_chart({'type': 'line'})
            chart4.add_series({
                'categories': ['HourlyCounts', 1, 0, len(df_hourly), 0],
                'values':     ['HourlyCounts', 1, 1, len(df_hourly), 1],
                'name': 'Requests per Hour'
            })
            chart4.set_title({'name': 'Hourly Requests'})
            worksheet.insert_chart('D2', chart4)

        print(f"\n✅ Excel 报告已生成: {output_path}")