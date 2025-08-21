from server import mcp
from datetime import datetime
import re

@mcp.tool()
def add(x: int, y: int) -> int:
    """
    返回兩個數字的和。
    
    參數：
        x (int): 第一個數字
        y (int): 第二個數字
    
    回傳：
        int: x 和 y 的和
    """
    return x + y

LOG_PATH = "../data/access_log_part1.log" 

@mcp.tool()
def filter_logs_by_time_and_status(start_time: str, end_time: str, status_code: str):
    """
    從固定路徑讀取 log，根據時間區間與單一 HTTP 狀態碼篩選。

    參數：
        start_time (str): 起始時間，格式 "dd/Mon/yyyy:HH:MM:SS"
        end_time (str): 結束時間，格式 "dd/Mon/yyyy:HH:MM:SS"
        status_code (str): 要篩選的 HTTP 狀態碼，例如 "404"

    回傳：
        list of str: 符合條件的 log 行
    """

    time_format = "%d/%b/%Y:%H:%M:%S"
    start_dt = datetime.strptime(start_time, time_format)
    end_dt = datetime.strptime(end_time, time_format)

    try:
        status_code = int(status_code)
    except ValueError:
        print(f"無效的狀態碼：{status_code}")
        return []

    filtered_logs = []

    try:
        with open(LOG_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.search(r'\[(.*?) \+\d{4}\]\s+"[^"]+"\s+(\d{3})', line)
                if not match:
                    continue

                timestamp_str = match.group(1)
                log_status = int(match.group(2))

                try:
                    log_dt = datetime.strptime(timestamp_str, time_format)
                except ValueError:
                    continue

                if start_dt <= log_dt <= end_dt and log_status == status_code:
                    filtered_logs.append(line.strip())

    except FileNotFoundError:
        print(f"找不到 log 檔案：{LOG_PATH}")
    except Exception as e:
        print(f"讀取 log 時發生錯誤：{e}")

    return filtered_logs


# result = filter_logs_by_time_and_status(
#     start_time="14/Jul/2025:00:00:00",
#     end_time="14/Jul/2025:23:59:59",
#     status_codes=[404]
# )

# for log in result:
#     print(log)