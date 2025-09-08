import re
from app.dspy_modules import IntentChecker, LogQueryExtractor, GeneralResponseGenerator, WebLogBriefResponseGenerator, WebLogDetailedResponseGenerator
import operator
from typing import TypedDict, Annotated, List, Dict
from app.tools.log_tools import filter_logs_by_time_and_status
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from datetime import datetime

from app.tools.ipinfo import get_ip_info

# === 初始化 DSPy 模組 ===
intent_checker = IntentChecker()

# === 定義狀態類型 ===
class AllState(TypedDict):
    messages: Annotated[List[Dict[str, str]], operator.add]
    tool_output: str
    tool_detail: str
    intent: str


# === 節點： 進行意圖判斷 ===
def intent_check(state: AllState) -> dict:
    user_input = state["messages"][-1]["content"]
    desc = "查詢IP也算是web_log"
    intent = intent_checker(question=user_input, intent_labels=["web_log", "general"], intent_desc=desc).intent
    print(f"使用者意圖: {intent}")
    print(f"user_input: {user_input}")

    # 根據意圖決定清空與否
    tool_output = [] if intent != "web_log" else state.get("tool_output", [])
    tool_detail = "" if intent != "web_log" else state.get("tool_detail", "")

    print(f"tool_output: {tool_output}")
    print(f"tool_detail: {tool_detail}")
    
    return {
        "next": "use_web_tool" if intent == "web_log" else "general",
        "intent": intent,
        "tool_output": tool_output,
        "tool_detail": tool_detail
    }

# === 節點： 工具執行 ===
def web_log_tool(state: AllState) -> dict:
    user_input = state["messages"][-1]["content"]
    log_query = LogQueryExtractor()

    # 使用 DSPy 模型提取時間範圍和狀態碼
    query_result = log_query(question=user_input)
    start_time = query_result.start_time
    end_time = query_result.end_time
    status_code = query_result.status_code
    http_method = query_result.http_method
    source_ip = query_result.source_ip

    print(f"提取時間範圍和狀態碼: {start_time} - {end_time}, {status_code}, {http_method}, {source_ip}")

    # 若時間未提供，補上今天的時間範圍
    if not start_time or not end_time:
        default_start, default_end = get_today_time_range()
        start_time = start_time or default_start
        end_time = end_time or default_end

    # 目前沒有真實資料，先用固定日期
    start_time = "14/Jul/2025:00:00:00"
    end_time = "14/Jul/2025:23:59:59"
    
    print(f"最終時間範圍和狀態碼: {start_time} - {end_time}, {status_code}, {http_method}, {source_ip}")


    # 根據提取的參數過濾日誌
    stats, logs, structured_logs = filter_logs_by_time_and_status(
        start_time=start_time,
        end_time=end_time,
        status_code=status_code,
        http_method=http_method,
        source_ip=source_ip
    )

    print(stats)
    print("過濾後的日誌數量:", len(logs))

    return {
        "tool_output": stats,
        "tool_detail": structured_logs
    }

def get_today_time_range():
    today = datetime.now()
    day_str = today.strftime("%d/%b/%Y")
    return (
        f"{day_str}:00:00:00",
        f"{day_str}:23:59:59"
    )

def check_use_ip_info_tool(state: AllState) -> bool:
    user_input = state["messages"][-1]["content"].lower()
    intent = intent_checker(question=user_input, intent_labels=["ip_info", "none"], intent_desc="").intent

    return {
        "next": True if intent == "ip_info" else False
    }

# === 節點： 查詢 IP 資訊 ===
def ip_info_tool(state: AllState) -> dict:
    user_input = state["messages"][-1]["content"].lower()
    ip_regex = r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}'
    ip_match = re.search(ip_regex, user_input)
    ip_address = ip_match.group(0)
    ip_info = get_ip_info(ip_address)
    tool_output = state.get("tool_output", "")
    tool_output += f"\nIP 資訊: {ip_info}"
    print(f"IP 資訊: {ip_info}")
    return {
        "tool_output": tool_output
    }


# === 節點： 一般回應 ===
def general_response(state: AllState) -> AllState:
    recent_messages = state["messages"][-6:]
    general_response_generator = GeneralResponseGenerator()
    answer = general_response_generator(question=recent_messages).answer

    return {
        "messages": [{"role": "assistant", "content": answer}]
    }

# === 節點： web log 簡答詳答判斷 ===
def web_log_response_classification(state: AllState) -> AllState:
    # 根據使用者的提問判斷要簡短回應還是詳細回應，使用
    user_input = state["messages"][-1]["content"].lower()
    intent = intent_checker(question=user_input, intent_labels=["brief", "detailed"], intent_desc="").intent
    print(f"使用者想要的回應類型: {intent}")
    
    return {
        "next": "brief" if intent == "brief" else "detailed"
    }


# === 節點： web log 工具簡短回應 ===
def web_log_brief_response(state: AllState) -> AllState:
    recent_messages = state["messages"][-6:]
    formatted_history = ""
    for msg in recent_messages:
        role = "使用者" if msg["role"] == "user" else "助理"
        formatted_history += f"{role}：{msg['content']}\n"

    tool_output = state.get("tool_output", "")

    web_log_brief_response_generator = WebLogBriefResponseGenerator()
    answer = web_log_brief_response_generator(chat_history=formatted_history, tool_output=tool_output).answer

    return {
        "messages": [{"role": "assistant", "content": answer}]
    }


# === 節點： web log 工具詳細回應 ===
def web_log_detailed_response(state: AllState) -> AllState:
    recent_messages = state["messages"][-6:]
    formatted_history = ""
    for msg in recent_messages:
        role = "使用者" if msg["role"] == "user" else "助理"
        formatted_history += f"{role}：{msg['content']}\n"

    tool_output = state.get("tool_output", "")
    
    web_log_detailed_response_generator = WebLogDetailedResponseGenerator()
    answer = web_log_detailed_response_generator(chat_history=formatted_history, tool_output=tool_output).answer

    return {
        "messages": [{"role": "assistant", "content": answer}]
    }


# === 定義 LangGraph 流程 ===
graph = StateGraph(AllState)

graph.add_node("intent_check", intent_check)
graph.add_node("web_log_tool", web_log_tool)
graph.add_node("get_ip_info", ip_info_tool)
graph.add_node("check_use_ip_info_tool", check_use_ip_info_tool)
graph.add_node("general_response", general_response)
graph.add_node("web_log_response_classification", web_log_response_classification)
graph.add_node("web_log_brief_response", web_log_brief_response)
graph.add_node("web_log_detailed_response", web_log_detailed_response)

graph.set_entry_point("intent_check")

graph.add_conditional_edges(
    "intent_check",
    lambda state: state["next"],
    {
        "use_web_tool": "web_log_tool",
        "general": "general_response"
    }
)

graph.add_edge("web_log_tool", "check_use_ip_info_tool")

graph.add_conditional_edges(
    "check_use_ip_info_tool",
    lambda state: state["next"],
    {
        True: "get_ip_info",
        False: "web_log_response_classification"
    }
)
graph.add_edge("get_ip_info", "web_log_response_classification")

graph.add_conditional_edges(
    "web_log_response_classification",
    lambda state: state["next"],
    {
        "brief": "web_log_brief_response",
        "detailed": "web_log_detailed_response"
    }
)

graph.add_edge("web_log_brief_response", END)
graph.add_edge("web_log_detailed_response", END)

memory = MemorySaver()
app = graph.compile(checkpointer=memory)
