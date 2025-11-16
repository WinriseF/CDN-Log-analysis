import os
import gzip
from collections import Counter
import re

MERGED_LOG = "merged_logs.log"
BLACKLIST_IP = "blacklist_ip.txt"
TOP_IP = "top_ip.txt"
SPIDER_LOG = "spiders.log"

# 常见扫描器关键字
SPIDER_KEYWORDS = [
    "CensysInspect",
    "curl",
    "Wget",
    "bot",
    "crawl",
    "scanner",
    "security",
    "nmap"
]

# 日志正则，和前面分析脚本一致
LOG_PATTERN = re.compile(
    r'\[(?P<time>.*?)\]\s+'
    r'(?P<ip>\S+)\s+'
    r'(?P<resp_time>\d+)\s+'
    r'"(?P<referer>.*?)"\s+'
    r'"(?P<protocol>.*?)"\s+'
    r'"(?P<method>.*?)"\s+'
    r'"(?P<domain>.*?)"\s+'
    r'"(?P<path>.*?)"\s+'
    r'(?P<status>\d+)\s+'
    r'(?P<size>\d+)\s+'
    r'(?P<hit>\S+)\s+'
    r'"(?P<ua>.*?)"\s+'
    r'"(?P<other>.*?)"\s+'
    r'(?P<source_ip>\S+)'
)

def parse_log_line(line):
    m = LOG_PATTERN.match(line)
    return m.groupdict() if m else None

def merge_gz_files():
    gz_files = sorted(f for f in os.listdir('.') if f.endswith('.gz'))

    if not gz_files:
        print("❌ 未找到任何 .gz 文件")
        return

    print(f"🔍 找到 {len(gz_files)} 个 .gz 文件，开始合并…")

    with open(MERGED_LOG, 'wb') as out_f:
        for gz_file in gz_files:
            print(f"➡ 合并：{gz_file}")
            with gzip.open(gz_file, 'rb') as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b''):
                    out_f.write(chunk)

    print(f"📦 合并完成：{MERGED_LOG}\n")

def detect_spider(ua):
    if not ua:
        return False
    ua_lower = ua.lower()
    return any(key.lower() in ua_lower for key in SPIDER_KEYWORDS)

def analyze_log():
    if not os.path.exists(MERGED_LOG):
        print("❌ merged_logs.log 不存在，请先合并日志！")
        return

    print("📊 开始分析日志…")

    ip_counter = Counter()
    spider_entries = []

    with open(MERGED_LOG, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            data = parse_log_line(line)
            if not data:
                continue

            ip_counter[data['ip']] += 1

            if detect_spider(data['ua']):
                spider_entries.append(line)

    # 输出 TOP 100 IP
    with open(TOP_IP, 'w', encoding='utf-8') as f:
        for ip, count in ip_counter.most_common(100):
            f.write(f"{ip} {count}\n")

    # 输出 spider 日志
    with open(SPIDER_LOG, 'w', encoding='utf-8') as f:
        f.writelines(spider_entries)

    # 生成黑名单（访问 100 次以上 或 属于扫描器）
    blacklist = set(ip for ip, count in ip_counter.items() if count > 100)
    blacklist.update(data['ip'] for line in spider_entries if (data := parse_log_line(line)))

    with open(BLACKLIST_IP, 'w', encoding='utf-8') as f:
        for ip in blacklist:
            if ip:
                f.write(ip + "\n")

    print(f"""
🎉 分析完成！

📌 访问量 TOP 100 IP：
    {TOP_IP}

📌 爬虫 & 扫描器日志：
    {SPIDER_LOG}

📌 自动生成黑名单：
    {BLACKLIST_IP}

✔ 支持 Censys / curl / Wget / nmap / 各类扫描器自动识别
✔ 支持大日志（流式处理）
""")

if __name__ == "__main__":
    merge_gz_files()
    analyze_log()
