import re
import pandas as pd

LOG_FILE = "merged_logs.log"
OUTPUT_XLSX = "logs_analysis.xlsx"

# 日志正则
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

# 1️⃣ 读取日志
rows = []
with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        data = parse_log_line(line)
        if data:
            rows.append(data)

# 2️⃣ 转 DataFrame
df = pd.DataFrame(rows)
df['status'] = df['status'].astype(int)
df['resp_time'] = df['resp_time'].astype(int)
df['size'] = df['size'].astype(int)

# 转 datetime 并去掉时区
df['time'] = pd.to_datetime(df['time'], format="%d/%b/%Y:%H:%M:%S %z", errors='coerce')
df['time'] = df['time'].dt.tz_convert(None)
df['hour'] = df['time'].dt.floor('h')

# 3️⃣ 状态码统计
status_counts = df['status'].value_counts().sort_index()

# 4️⃣ Top IP
top_ips = df['ip'].value_counts().head(20)

# 4️⃣1️⃣ Top IP 2XX 占比
top_ip_status = []
for ip, _ in top_ips.items():
    ip_df = df[df['ip'] == ip]
    total = len(ip_df)
    count_2xx = ip_df[ip_df['status'].between(200, 299)].shape[0]
    ratio = round(count_2xx / total * 100, 2) if total > 0 else 0
    top_ip_status.append({'ip': ip, 'total_requests': total, '2xx_requests': count_2xx, '2xx_ratio(%)': ratio})
top_ip_status_df = pd.DataFrame(top_ip_status)

# 5️⃣ 按小时访问量
hourly_counts = df.groupby('hour').size()

# 6️⃣ 写入 Excel 并插入图表
with pd.ExcelWriter(OUTPUT_XLSX, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='RawLogs', index=False)
    
    workbook  = writer.book

    # --- 状态码分布 ---
    status_counts.to_frame('count').to_excel(writer, sheet_name='StatusCounts')
    worksheet = writer.sheets['StatusCounts']
    chart1 = workbook.add_chart({'type': 'column'})
    chart1.add_series({
        'categories': ['StatusCounts', 1, 0, len(status_counts), 0],
        'values':     ['StatusCounts', 1, 1, len(status_counts), 1],
        'name': 'Status Code Count'
    })
    chart1.set_title({'name': 'Status Code Distribution'})
    chart1.set_x_axis({'name': 'Status Code'})
    chart1.set_y_axis({'name': 'Count'})
    worksheet.insert_chart('D2', chart1)

    # --- Top IP ---
    top_ips.to_frame('count').to_excel(writer, sheet_name='TopIPs')
    worksheet = writer.sheets['TopIPs']
    chart2 = workbook.add_chart({'type': 'column'})
    chart2.add_series({
        'categories': ['TopIPs', 1, 0, len(top_ips), 0],
        'values':     ['TopIPs', 1, 1, len(top_ips), 1],
        'name': 'Top IPs'
    })
    chart2.set_title({'name': 'Top 20 IPs'})
    chart2.set_x_axis({'name': 'IP'})
    chart2.set_y_axis({'name': 'Count'})
    worksheet.insert_chart('D2', chart2)

    # --- Top IP 2XX 占比 ---
    top_ip_status_df.to_excel(writer, sheet_name='TopIP_2XX', index=False)
    worksheet = writer.sheets['TopIP_2XX']
    chart3 = workbook.add_chart({'type': 'column'})
    chart3.add_series({
        'categories': ['TopIP_2XX', 1, 0, len(top_ip_status_df), 0],
        'values':     ['TopIP_2XX', 1, 3, len(top_ip_status_df), 3],  # 2xx_ratio(%) 列
        'name': '2XX Ratio'
    })
    chart3.set_title({'name': 'Top IP 2XX Ratio (%)'})
    chart3.set_x_axis({'name': 'IP'})
    chart3.set_y_axis({'name': '2XX Ratio (%)'})
    worksheet.insert_chart('E2', chart3)

    # --- 按小时访问量 ---
    hourly_counts.to_frame('count').to_excel(writer, sheet_name='HourlyCounts')
    worksheet = writer.sheets['HourlyCounts']
    chart4 = workbook.add_chart({'type': 'line'})
    chart4.add_series({
        'categories': ['HourlyCounts', 1, 0, len(hourly_counts), 0],
        'values':     ['HourlyCounts', 1, 1, len(hourly_counts), 1],
        'name': 'Requests per Hour'
    })
    chart4.set_title({'name': 'Hourly Requests'})
    chart4.set_x_axis({'name': 'Hour'})
    chart4.set_y_axis({'name': 'Count'})
    worksheet.insert_chart('D2', chart4)

print(f"日志分析完成，输出文件: {OUTPUT_XLSX}")
