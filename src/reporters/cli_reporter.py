from src.config import AppConfig
from src.reporters.base import BaseReporter

class CliReporter(BaseReporter):
    """将分析结果摘要输出到命令行"""
    def generate(self):
        print("\n--- CDN 日志分析摘要 ---")
        
        # 检查 'basic_stats' 结果是否存在
        if 'basic_stats' in self.results:
            stats = self.results['basic_stats']
            
            print("\n[+] 状态码分布:")
            print(stats['status_counts'].to_string())
            
            print(f"\n[+] Top {self.config.analysis.top_n_count} IP 地址:")
            print(stats['top_ips'].to_string())

            print(f"\n[+] Top {self.config.analysis.top_n_count} IP 2xx成功率:")
            print(stats['top_ip_status'].to_string())
            
            print("\n[+] 每小时请求数:")
            print(stats['hourly_counts'].to_string())
        
        if 'geo_ip' in self.results and self.results['geo_ip']:
            geo_stats = self.results['geo_ip']
            
            # --- 打印运营商统计 ---
            if 'isp' in geo_stats['ip_geo_details'].columns:
                isp_counts = geo_stats['ip_geo_details'].groupby('isp')['count'].sum().sort_values(ascending=False)
                print(f"\n[+] Top {self.config.analysis.top_n_count} 运营商:")
                print(isp_counts.head(self.config.analysis.top_n_count).to_string())

            print(f"\n[+] Top {self.config.analysis.top_n_count} 来源国家/地区:")
            print(geo_stats['country_counts'].to_string())
        
        print("\n--- 报告结束 ---\n")