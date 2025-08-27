from app.dspy_modules import IntentChecker, LogQueryExtractor, ResponseGenerator
import operator
from typing import TypedDict, Annotated, List, Dict
from app.tools.log_tools import filter_logs_by_time_and_status
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from datetime import datetime

# === 初始化 DSPy 模組 ===
intent_checker = IntentChecker()
response_generator = ResponseGenerator()

# === 定義狀態類型 ===
class AllState(TypedDict):
    messages: Annotated[List[Dict[str, str]], operator.add]
    tool_output: str
    tool_detail: str
    intent: str


# === 節點 1：DSPy 進行意圖判斷 ===
def intent_check(state: AllState) -> dict:
    user_input = state["messages"][-1]["content"]
    intent = intent_checker(question=user_input).intent
    
    # 根據意圖決定清空與否
    tool_output = "" if intent != "log" else state.get("tool_output", "")
    tool_detail = "" if intent != "log" else state.get("tool_detail", "")

    return {
        "next": "use_tool" if intent == "log" else "no_tool",
        "intent": intent,
        "tool_output": tool_output,
        "tool_detail": tool_detail
    }

# === 節點 2：工具執行 ===
def web_log_tool_node(state: AllState) -> dict:
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

# === 節點 3：使用 DSPy 產生回應 ===
def llm_response(state: AllState) -> AllState:
    recent_messages = state["messages"][-6:]
    formatted_history = ""
    for msg in recent_messages:
        role = "使用者" if msg["role"] == "user" else "助理"
        formatted_history += f"{role}：{msg['content']}\n"

    tool_output = state.get("tool_output", "")
    answer = response_generator(chat_history=formatted_history, tool_output=tool_output).answer

    return {
        "messages": [{"role": "assistant", "content": answer}]
    }

# === 定義 LangGraph 流程 ===
graph = StateGraph(AllState)

graph.add_node("intent_check", intent_check)
graph.add_node("web_log_tool_node", web_log_tool_node)
graph.add_node("llm_response", llm_response)

graph.set_entry_point("intent_check")

graph.add_conditional_edges(
    "intent_check",
    lambda state: state["next"],
    {
        "use_tool": "web_log_tool_node",
        "no_tool": "llm_response"
    }
)

graph.add_edge("web_log_tool_node", "llm_response")
graph.add_edge("llm_response", END)

memory = MemorySaver()
app = graph.compile(checkpointer=memory)
