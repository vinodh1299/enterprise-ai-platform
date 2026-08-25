from typing import Optional, List
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """
    Represents a single message in a conversation thread.
    Roles: 'system', 'user', 'assistant'
    """
    role: str = Field(..., description="Role of message sender: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Text content of the message")


class AIChatRequest(BaseModel):
    """
    Request schema for direct LLM chat endpoint (POST /api/ai/chat).
    """
    prompt: str = Field(..., description="The user's query or message", min_length=1)
    system_instruction: Optional[str] = Field(
        default="You are a helpful Enterprise AI assistant. Be concise, professional, and accurate.",
        description="System prompt defining AI behavior and persona"
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Creativity vs deterministic control (0.0 = strict/factual, 1.0+ = creative)"
    )
    history: Optional[List[ChatMessage]] = Field(
        default=[],
        description="Optional prior conversation turns for context retention"
    )


class AIChatResponse(BaseModel):
    """
    Response schema returning the AI answer, token metrics, and cost estimations.
    """
    answer: str
    model_name: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float
