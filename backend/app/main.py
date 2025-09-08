from typing import Dict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.api.web_log.api import router as web_log_router
from app.graph import app as langgraph_app

app = FastAPI(title="Agent App")

# ✅ CORS 中介層
origins = [
    "http://localhost:4200",
    "https://thriving-alfajores-e1c9ee.netlify.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 掛載 API 路由
app.include_router(web_log_router)

# ✅ 使用者輸入格式
class UserInput(BaseModel):
    input: str
    session_id: str

session_states: Dict[str, dict] = {}


@app.options("/api/infer")
async def preflight_handler(request: Request):
    return JSONResponse(
        content={"message": "CORS preflight OK"},
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin") or "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": request.headers.get("Access-Control-Request-Headers", "*"),
        },
    )

@app.post("/api/infer")
async def run_graph_with_simple_input(user_input: UserInput):
    session_id = user_input.session_id

    # 初始化 session 狀態
    if session_id not in session_states:
        session_states[session_id] = {
            "messages": [],
        }

    current_state = {
        "messages": [
            {"role": "user", "content": user_input.input}
        ]
    }

    result = langgraph_app.invoke(current_state, config={"thread_id": session_id})

    # 更新 session 狀態（儲存完整訊息）
    session_states[session_id]["messages"] = result["messages"]
    if "tool_output" in result:
        session_states[session_id]["tool_output"] = result["tool_output"]
    if "tool_detail" in result:
        session_states[session_id]["tool_detail"] = result["tool_detail"]

    # 回傳只有最後一則訊息與其他資料
    response = {
        "message": result["messages"][-1]
    }
    if "tool_output" in result:
        response["tool_output"] = result["tool_output"]
    if "tool_detail" in result:
        response["tool_detail"] = result["tool_detail"]

    return response
