from datetime import datetime
import re

LOG_PATH = "./data/access_log_part1.log" 


def filter_logs_by_time_and_status(start_time: str, end_time: str, status_code: str):
    """
    從固定路徑讀取 log，根據時間區間與單一 HTTP 狀態碼篩選，回傳摘要與部分結果。

    參數：
        start_time (str): 起始時間，格式 "dd/Mon/yyyy HH:MM:SS"
        end_time (str): 結束時間，格式 "dd/Mon/yyyy HH:MM:SS"
        status_code (str): 要篩選的 HTTP 狀態碼（例如 "404"）

    回傳：
        list of str: 摘要 + 範例 log 行
    """

    time_format = "%d/%b/%Y:%H:%M:%S"
    
    try:
        start_dt = datetime.strptime(start_time, time_format)
        end_dt = datetime.strptime(end_time, time_format)
    except ValueError as e:
        return [f"❗ 時間格式錯誤：{e}"]

    try:
        status_code_int = int(status_code)
    except ValueError:
        return [f"❗ 無效的狀態碼：{status_code}"]

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

                if start_dt <= log_dt <= end_dt and log_status == status_code_int:
                    filtered_logs.append(line.strip())

    except FileNotFoundError:
        return [f"❗ 找不到 log 檔案：{LOG_PATH}"]
    except Exception as e:
        return [f"❗ 讀取 log 時發生錯誤：{e}"]

    if not filtered_logs:
        return ["🔍 在指定時間範圍內沒有找到符合條件的日誌。"]

    summary = f"✅ 共找到 {len(filtered_logs)} 筆符合條件的日誌。"
    sample_logs = filtered_logs
    return [summary] + sample_logs


result = filter_logs_by_time_and_status(
    start_time="14/Jul/2025:00:00:00",
    end_time="14/Jul/2025:23:59:59",
    status_code="404"
)

for log in result:
    print(log)