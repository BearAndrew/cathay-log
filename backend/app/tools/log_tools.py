from datetime import datetime
import re
import os
from collections import defaultdict, Counter

# 自動取得 log 檔的絕對路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "../data/access_log_part2.log")

def filter_logs_by_time_and_status(start_time: str, end_time: str, status_code: str = None,
                                   http_method: str = None, source_ip: str = None):
    """
    回傳：
        Tuple[str, list[str], dict]: 統計資訊、原始 log line、結構化 table 資料
    """

    time_format = "%d/%b/%Y:%H:%M:%S"

    try:
        start_dt = datetime.strptime(start_time, time_format)
        end_dt = datetime.strptime(end_time, time_format)
    except ValueError:
        print("時間格式錯誤")
        return "", [], {}

    # 永遠排除 2xx 狀態碼
    exclude_2xx = re.compile(r"^(?!2\d\d$)")

    # 編譯 status_code 正規表達式
    try:
        if status_code:
            user_status_pattern = re.compile(status_code)
            def combined_status_filter(code_str):
                return exclude_2xx.match(code_str) and user_status_pattern.match(code_str)
        else:
            def combined_status_filter(code_str):
                return exclude_2xx.match(code_str)
    except re.error:
        print(f"無效的 status_code 正規表達式：{status_code}")
        return "", [], {}

    # 編譯 http_method 正規表達式
    try:
        http_method_pattern = re.compile(http_method) if http_method else None
    except re.error:
        print(f"無效的 http_method 正規表達式：{http_method}")
        return "", [], {}

    # 編譯 source_ip 正規表達式
    try:
        source_ip_pattern = re.compile(source_ip) if source_ip else None
    except re.error:
        print(f"無效的 source_ip 正規表達式：{source_ip}")
        return "", [], {}

    filtered_logs = []
    structured_body = []

    # 統計資料結構
    ip_counter = Counter()
    status_counter = Counter()
    ip_to_resources = defaultdict(Counter)
    resource_counter = Counter()

    try:
        with open(LOG_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.search(
                    r'\[(?P<time>.*?) \+\d{4}\] '
                    r'"(?P<method>[A-Z]+) (?P<resource>[^ ]+) HTTP/[^"]+" (?P<status>\d{3})',
                    line
                )
                if not match:
                    continue

                timestamp_str = match.group("time")
                method = match.group("method")
                resource = match.group("resource")
                log_status = int(match.group("status"))

                # 從行尾取來源 IP
                parts = line.strip().split()
                if len(parts) < 1:
                    continue
                real_ip = parts[-1]

                try:
                    log_dt = datetime.strptime(timestamp_str, time_format)
                except ValueError:
                    continue

                # 條件過濾
                if not (start_dt <= log_dt <= end_dt):
                    continue
                if not combined_status_filter(str(log_status)):
                    continue
                if http_method_pattern and not http_method_pattern.match(method):
                    continue
                if source_ip_pattern and not source_ip_pattern.match(real_ip):
                    continue

                filtered_logs.append(line.strip())

                structured_body.append({
                    "timestamp": timestamp_str,
                    "resource": resource,
                    "source_ip": real_ip,
                    "http_method": method,
                    "status_code": log_status
                })

                ip_counter[real_ip] += 1
                ip_to_resources[real_ip][resource] += 1
                resource_counter[resource] += 1
                status_counter[log_status] += 1

    except FileNotFoundError:
        print(f"找不到 log 檔案：{LOG_PATH}")
        return "", [], {}
    except Exception as e:
        print(f"讀取 log 時發生錯誤：{e}")
        return "", [], {}

    # 統計資訊文字
    stats_summary = []

    stats_summary.append("📊 前 10 名請求次數最多的 IP：")
    for ip, count in ip_counter.most_common(10):
        top_resources = ip_to_resources[ip].most_common(5)
        resources_str = ", ".join([f"{res} ({c}次)" for res, c in top_resources])
        stats_summary.append(f"- IP：{ip} | 請求次數：{count} | 資源：{resources_str}")

    stats_summary.append("\n📊 前 10 名被請求最多的資源：")
    for resource, count in resource_counter.most_common(10):
        stats_summary.append(f"- 資源：{resource} | 請求次數：{count}")
        
    stats_summary.append("\n📊 各狀態碼出現次數：")
    for status, count in sorted(status_counter.items()):
        stats_summary.append(f"- 狀態碼：{status} | 次數：{count}")


    # 結構化資料格式（僅前 100 筆）
    structured_table = {
        "type": "table",
        "data": {
            "headers": [
                {"key": "timestamp", "label": "時間"},
                {"key": "resource", "label": "請求資源"},
                {"key": "source_ip", "label": "來源 IP"},
                {"key": "http_method", "label": "HTTP 方法"},
                {"key": "status_code", "label": "狀態碼"},
            ],
            "body": structured_body[:100]
        }
    }

    return "\n".join(stats_summary), filtered_logs, structured_table
