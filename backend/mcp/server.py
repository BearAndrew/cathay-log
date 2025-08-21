"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

from datetime import datetime
import re
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

LOG_PATH = "./data/access_log_part1.log" 

@mcp.tool()
def filter_logs_by_time_and_status(start_time: str, end_time: str, status_code: str):
    """
    從固定路徑讀取 log，根據時間區間與單一 HTTP 狀態碼篩選，回傳摘要與部分結果。

    參數：
        start_time (str): 起始時間，格式 "dd/Mon/yyyy:HH:MM:SS"
        end_time (str): 結束時間，格式 "dd/Mon/yyyy:HH:MM:SS"
        status_code (str): 要篩選的 HTTP 狀態碼（例如 "404"）

    回傳：
        list of str: 所有符合條件的 log
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

    return filtered_logs


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# Add a prompt
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."
  
if __name__ == "__main__":
    mcp.run(transport="sse")
