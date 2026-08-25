from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """
    Request schema for AI Agent endpoint (POST /api/ai/agent/chat).
    """
    prompt: str = Field(..., description="The user request requiring agent reasoning and tool usage", min_length=1)


class ToolCallStep(BaseModel):
    """
    Record of a single tool execution step by the agent.
    """
    step_number: int
    tool_name: str
    tool_args: Dict[str, Any]
    tool_result: str


class AgentResponse(BaseModel):
    """
    Response schema returning the final agent answer and full trace of executed tools.
    """
    answer: str
    tool_calls: List[ToolCallStep]
    iterations: int
    model_name: str
    total_tokens: int
    estimated_cost_usd: float
