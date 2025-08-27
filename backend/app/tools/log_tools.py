from datetime import datetime
import re
import os
from collections import defaultdict, Counter

# 自動取得 log 檔的絕對路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "../data/access_log_part2.log")

def filter_logs_by_time_and_status(start_time: str, end_time: str, status_code: str,
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

    try:
        status_code = int(status_code)
    except ValueError:
        print(f"無效的狀態碼：{status_code}")
        return "", [], {}

    filtered_logs = []
    structured_body = []

    # 統計資料結構
    ip_counter = Counter()
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

                if not (start_dt <= log_dt <= end_dt):
                    continue
                if log_status != status_code:
                    continue
                if http_method and method != http_method.upper():
                    continue
                if source_ip and real_ip != source_ip:
                    continue

                filtered_logs.append(line.strip())

                # 結構化資料儲存
                structured_body.append({
                    "timestamp": timestamp_str,
                    "resource": resource,
                    "source_ip": real_ip,
                    "status_code": log_status
                })

                ip_counter[real_ip] += 1
                ip_to_resources[real_ip][resource] += 1
                resource_counter[resource] += 1

    except FileNotFoundError:
        print(f"找不到 log 檔案：{LOG_PATH}")
        return "", [], {}
    except Exception as e:
        print(f"讀取 log 時發生錯誤：{e}")
        return "", [], {}

    # 統計資訊
    stats_summary = []

    stats_summary.append("📊 前 10 名請求次數最多的 IP：")
    for ip, count in ip_counter.most_common(10):
        top_resources = ip_to_resources[ip].most_common(5)
        resources_str = ", ".join([f"{res} ({c}次)" for res, c in top_resources])
        stats_summary.append(f"- IP：{ip} | 請求次數：{count} | 資源：{resources_str}")

    stats_summary.append("\n📊 前 10 名被請求最多的資源：")
    for resource, count in resource_counter.most_common(10):
        stats_summary.append(f"- 資源：{resource} | 請求次數：{count}")

    # 建立結構化資料格式
    structured_table = {
        "type": "table",
        "data": {
            "headers": [
                { "key": "timestamp", "label": "時間" },
                { "key": "resource", "label": "請求資源" },
                { "key": "source_ip", "label": "來源 IP" },
                { "key": "status_code", "label": "狀態碼" }
            ],
            "body": structured_body
        }
    }

    return "\n".join(stats_summary), filtered_logs, structured_table
