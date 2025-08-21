from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# ========== 定義請求與回應模型 ==========
class AgentInput(BaseModel):
    input: str

class ToolCallInfo(BaseModel):
    name: str
    args: dict
    tool_call_id: Optional[str] = None

class MessageInfo(BaseModel):
    type: str  # "user", "ai", "system", etc.
    content: Optional[str]
    tool_calls: Optional[List[ToolCallInfo]] = []

class AgentResponse(BaseModel):
    response: str
    all_contents: List[MessageInfo]

# ========== 全域變數 ==========
agent = None  # type: ignore

# ========== 在 FastAPI 啟動時初始化 Agent ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    client = MultiServerMCPClient(
        {
            "math": {
                "url": "http://localhost:8000/sse",
                "transport": "sse",
            }
        }
    )
    tools = await client.get_tools()

    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        api_key=api_key,
    )
    agent = create_react_agent(model, tools)

    print("✅ Agent initialized.")
    yield
    print("🛑 Shutting down...")

# ======== App 實例建立 =========
app = FastAPI(lifespan=lifespan)

# ========== API 路由 ==========
@app.post("/agent/invoke", response_model=AgentResponse)
async def invoke_agent(user_input: AgentInput):
    global agent
    if agent is None:
        return JSONResponse(content={"error": "Agent not initialized"}, status_code=500)

    result = await agent.ainvoke({"messages": user_input.input})
    messages = result["messages"]

    all_contents: List[MessageInfo] = []

    for message in messages:
        msg_type = getattr(message, "type", "unknown")
        msg_content = getattr(message, "content", None)

        msg_tool_calls = []
        if hasattr(message, "tool_calls") and message.tool_calls:
            for call in message.tool_calls:
                tool_info = ToolCallInfo(
                    name=call["name"],
                    args=call["args"],
                    tool_call_id=getattr(call, "id", None)
                )
                msg_tool_calls.append(tool_info)

        all_contents.append(MessageInfo(
            type=msg_type,
            content=msg_content,
            tool_calls=msg_tool_calls
        ))

    # 擷取最後一段 AI 回應
    final_content = ""
    for msg in reversed(all_contents):
        if msg.type == "ai" and msg.content:
            final_content = msg.content
            break

    return AgentResponse(
        response=final_content,
        all_contents=all_contents
    )