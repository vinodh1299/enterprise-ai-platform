from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ConversationCreate(BaseModel):
    """
    Schema for creating a new conversation session.
    """
    title: Optional[str] = Field("New Conversation", description="Optional conversation title")


class MessageResponse(BaseModel):
    """
    Pydantic schema for returning chat messages.
    """
    id: int
    conversation_id: int
    role: str
    content: str
    tokens: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    """
    Pydantic schema for returning conversation session details.
    """
    id: int
    title: str
    user_id: int
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class MultiTurnChatRequest(BaseModel):
    """
    Request schema for sending a message in an existing conversation.
    """
    prompt: str = Field(..., description="User message prompt", min_length=1)


class MultiTurnChatResponse(BaseModel):
    """
    Response schema returning assistant response, active memory window count, and total tokens.
    """
    conversation_id: int
    user_message: MessageResponse
    assistant_message: MessageResponse
    active_memory_window_count: int
    rolling_summary: Optional[str] = None
    model_name: str
    total_tokens: int
    estimated_cost_usd: float
