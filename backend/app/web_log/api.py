from fastapi import APIRouter
from fastapi.responses import JSONResponse
from .model import AgentInput, AgentResponse
from .agent import invoke_agent_logic

router = APIRouter(prefix="/web-log", tags=["Web Log Agent"])

@router.post("/invoke", response_model=AgentResponse)
async def invoke_agent_endpoint(user_input: AgentInput):
    try:
        return await invoke_agent_logic(user_input)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
