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
        
        print("\n--- 报告结束 ---\n")