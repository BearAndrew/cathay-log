from app.dspy_modules import IntentChecker, ResponseGenerator
import operator
from typing import TypedDict, Annotated, List, Dict
from app.tools.log_tools import filter_logs_by_time_and_status
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# === 初始化 DSPy 模組 ===
intent_checker = IntentChecker()
response_generator = ResponseGenerator()

# === 定義狀態類型 ===
class AllState(TypedDict):
    messages: Annotated[List[Dict[str, str]], operator.add]
    tool_output: str
    intent: str

# === 節點 1：接收輸入 ===
def agent(state: AllState) -> AllState:
    return {}

# === 節點 2：DSPy 進行意圖判斷 ===
def intent_check(state: AllState) -> dict:
    user_input = state["messages"][-1]["content"]
    intent = intent_checker(question=user_input).intent
    
    # 根據意圖決定清空與否
    tool_output = "" if intent != "log" else state.get("tool_output", "")

    return {
        "next": "use_tool" if intent == "log" else "no_tool",
        "intent": intent,
        "tool_output": tool_output,  # 用 return 更新才有效
    }

# === 節點 3：工具執行 ===
def tool_node(state: AllState) -> dict:
    logs = filter_logs_by_time_and_status(
        start_time='14/Jul/2025:00:00:00',
        end_time='14/Jul/2025:23:59:59',
        status_code='404'
    )
    return {"tool_output": "\n".join(logs)}

# === 節點 4：使用 DSPy 產生回應 ===
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

graph.add_node("agent", agent)
graph.add_node("intent_check", intent_check)
graph.add_node("tool_node", tool_node)
graph.add_node("llm_response", llm_response)

graph.set_entry_point("agent")

graph.add_edge("agent", "intent_check")

graph.add_conditional_edges(
    "intent_check",
    lambda state: state["next"],
    {
        "use_tool": "tool_node",
        "no_tool": "llm_response"
    }
)

graph.add_edge("tool_node", "llm_response")
graph.add_edge("llm_response", END)

memory = MemorySaver()
app = graph.compile(checkpointer=memory)
