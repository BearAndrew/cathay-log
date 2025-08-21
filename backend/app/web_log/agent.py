from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import PromptTemplate

from app.config import GOOGLE_API_KEY
from .model import AgentInput, AgentResponse, MessageInfo, ToolCallInfo
from typing import List

agent = None # web log agent

async def initialize_agent():
    global agent
    if agent is not None:
        return

    try:
        client = MultiServerMCPClient(
            {
                "math": {
                    "url": "http://localhost:8000/sse",
                    "transport": "sse",
                }
            }
        )
        tools = await client.get_tools()

    except Exception as e:
        raise RuntimeError(f"MCP 工具加載失敗，請檢查 MCP 服務是否啟動")
    
    
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        api_key=GOOGLE_API_KEY,
    )
    prompt = """
        請使用{tools}工具來檢查伺服器狀態，伺服器資訊都可以從{tools}工具中獲取。
    """
    agent = create_react_agent(model, tools, prompt=prompt)
    print("✅ Web Log Agent initialized.")
    print(f"Available tools: {[tool.name for tool in tools]}")


async def invoke_agent_logic(user_input: AgentInput) -> AgentResponse:
    global agent
    if agent is None:
        await initialize_agent()

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

    final_content = ""
    for msg in reversed(all_contents):
        if msg.type == "ai" and msg.content:
            final_content = msg.content
            break

    return AgentResponse(
        response=final_content,
        all_contents=all_contents
    )
