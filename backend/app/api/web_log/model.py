from pydantic import BaseModel
from typing import List, Optional

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
