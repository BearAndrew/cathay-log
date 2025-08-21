import operator
from typing import TypedDict, Annotated, List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from app.config import GOOGLE_API_KEY  # 從 config.py 匯入 API 金鑰
from app.tools.log_tools import filter_logs_by_time_and_status 
from langgraph.checkpoint.memory import MemorySaver
import json

# === 定義狀態類型 ===
class AllState(TypedDict):
    messages: Annotated[List[Dict[str, str]], operator.add]
    tool_output: str  # 工具結果輸出，供後續 LLM 回應用

# === 初始化模型 ===
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",   # 模型名稱
    api_key=GOOGLE_API_KEY,     # API 金鑰
)


# === 節點 1：初始代理，接收使用者輸入 ===
def agent(state: AllState) -> AllState:
    return {}  # 初始節點什麼都不做，只接收輸入

# === 節點 2：意圖判斷 ===
def intent_check(state: AllState) -> dict:
    user_input = state["messages"][-1]["content"]
    if "log" in user_input or "404" in user_input or "日誌" in user_input:
        return {"next": "use_tool"}
    return {"next": "no_tool"}

# === 節點 3：tool 節點（取得log工具） ===
def tool_node(state: AllState) -> dict:
    start_time = '14/Jul/2025:00:00:00'
    end_time = '14/Jul/2025:23:59:59'
    status_code = '404'

    # 調用你已經實作好的工具函數
    logs = filter_logs_by_time_and_status(start_time, end_time, status_code)
    return {"tool_output": "\n".join(logs)}  # 日誌

# === 節點 4：LLM 整合輸出 ===
def llm_response(state: AllState) -> AllState:
    # 取最近 3 輪 user/assistant 對話（最多 6 則 message）
    recent_messages = state["messages"][-6:]
    formatted_history = ""
    for msg in recent_messages:
        role = "使用者" if msg["role"] == "user" else "助理"
        formatted_history += f"{role}：{msg['content']}\n"

    prompt = ChatPromptTemplate.from_template("""
    你是一個專業的伺服器維運人員，以下是最近幾輪對話：
    ---
    {chat_history}
    ---

    請根據這些對話與以下資訊，回答使用者的最新提問。
    如果有工具回傳資訊如下：
    ---
    {tool_output}

    若使用者詢問的是伺服器日誌相關問題，請根據工具輸出進行回答，並提供詳細建議與統計表格。
    若使用者沒有詢問伺服器日誌相關問題，請給予一般性回應。
    """)

    response_chain = prompt | model

    response = response_chain.invoke({
        "chat_history": formatted_history,
        "tool_output": state.get("tool_output", "")
    })

    return {
        "messages": [{"role": "assistant", "content": response.content}]
    }


# === 定義 LangGraph 流程 ===
graph = StateGraph(AllState)

graph.add_node("agent", agent)
graph.add_node("intent_check", intent_check)
graph.add_node("tool_node", tool_node)
graph.add_node("llm_response", llm_response)

graph.set_entry_point("agent")

graph.add_edge("agent", "intent_check")

# 根據意圖決定接下來流程
graph.add_conditional_edges(
    "intent_check",
    lambda state: state["next"],  # 解出下一個狀態名稱
    {
        "use_tool": "tool_node",
        "no_tool": "llm_response"
    }
)

# 工具使用後 → 回應
graph.add_edge("tool_node", "llm_response")
graph.add_edge("llm_response", END)

memory = MemorySaver()
app = graph.compile(checkpointer=memory)
