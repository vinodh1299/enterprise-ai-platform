from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    MessageResponse,
    MultiTurnChatRequest,
    MultiTurnChatResponse,
)
from app.ai.memory.manager import (
    get_conversation_memory,
    add_message_to_db,
    maybe_summarize_conversation,
)
from app.ai.llm.client import llm_client

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse, tags=["Conversation Memory"])
async def create_conversation(
    request: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new multi-turn conversation session.
    """
    conv = Conversation(
        title=request.title or "New Conversation",
        user_id=current_user.id
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)

    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        user_id=conv.user_id,
        summary=conv.summary,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=0
    )


@router.get("/conversations", response_model=List[ConversationResponse], tags=["Conversation Memory"])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all active conversation sessions owned by the authenticated user.
    """
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()

    response: List[ConversationResponse] = []
    for c in conversations:
        count_res = await db.execute(select(func.count(Message.id)).where(Message.conversation_id == c.id))
        msg_count = count_res.scalar() or 0

        response.append(ConversationResponse(
            id=c.id,
            title=c.title,
            user_id=c.user_id,
            summary=c.summary,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=msg_count
        ))

    return response


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse], tags=["Conversation Memory"])
async def get_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch complete message history for a conversation session.
    """
    # Verify ownership
    conv = await db.get(Conversation, conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Conversation #{conversation_id} not found.")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    return result.scalars().all()


@router.post("/conversations/{conversation_id}/chat", response_model=MultiTurnChatResponse, tags=["Conversation Memory"])
async def multi_turn_chat(
    conversation_id: int,
    request: MultiTurnChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Stateful Multi-Turn Chat Endpoint:
    Automatically retrieves previous message context window & rolling summary,
    passes memory history to LLM client, records new user & assistant messages,
    and handles automatic conversation summarization.
    """
    try:
        conv, summary, history = await get_conversation_memory(
            db=db,
            conversation_id=conversation_id,
            user_id=current_user.id,
            max_recent_messages=10
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    # Save user message to database
    user_msg_db = await add_message_to_db(
        db=db,
        conversation_id=conversation_id,
        role="user",
        content=request.prompt,
        tokens=len(request.prompt.split())
    )

    system_inst = "You are an Enterprise AI Assistant with stateful multi-turn conversation memory."
    if summary:
        system_inst += f"\nPREVIOUS CONVERSATION SUMMARY:\n{summary}"

    llm_resp = await llm_client.generate_chat_response(
        prompt=request.prompt,
        system_instruction=system_inst,
        temperature=0.7,
        history=history
    )

    # Save assistant response to database
    assistant_msg_db = await add_message_to_db(
        db=db,
        conversation_id=conversation_id,
        role="assistant",
        content=llm_resp.answer,
        tokens=llm_resp.output_tokens
    )

    # Check and perform rolling summarization if message threshold exceeded
    await maybe_summarize_conversation(db=db, conversation_id=conversation_id, threshold=12)

    return MultiTurnChatResponse(
        conversation_id=conversation_id,
        user_message=MessageResponse.model_validate(user_msg_db),
        assistant_message=MessageResponse.model_validate(assistant_msg_db),
        active_memory_window_count=len(history) + 2,
        rolling_summary=conv.summary,
        model_name=llm_resp.model_name,
        total_tokens=llm_resp.total_tokens,
        estimated_cost_usd=llm_resp.estimated_cost_usd
    )
