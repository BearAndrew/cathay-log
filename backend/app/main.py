from typing import Dict
from fastapi import FastAPI
from app.web_log.api import router as web_log_router
from pydantic import BaseModel
from app.graph import app as langgraph_app


app = FastAPI(title="Agent App")

# 掛載功能路由
app.include_router(web_log_router)



# === 自訂輸入格式 ===
class UserInput(BaseModel):
    input: str
    session_id: str
    
session_states: Dict[str, dict] = {}

@app.post("/api/infer")
async def run_graph_with_simple_input(user_input: UserInput):
    session_id = user_input.session_id

    # 初始化狀態（如該 session_id 沒有記錄）
    if session_id not in session_states:
        session_states[session_id] = {
            "messages": [],
            "tool_output": ""
        }

    # 準備這次的狀態（加入新的 user message）
    current_state = {
        "messages": [
            {"role": "user", "content": user_input.input}
        ],
        "tool_output": session_states[session_id]["tool_output"]
    }

    # 傳入 LangGraph 執行
    result = langgraph_app.invoke(current_state, config={"thread_id": session_id})

    # ✅ 直接覆蓋歷史，避免手動 append 重複
    session_states[session_id]["messages"] = result["messages"]

    # ✅ 更新工具輸出（如有）
    if "tool_output" in result:
        session_states[session_id]["tool_output"] = result["tool_output"]

    return result