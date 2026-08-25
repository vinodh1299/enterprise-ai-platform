import logging
from typing import Tuple, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.conversation import Conversation, Message
from app.schemas.ai import ChatMessage
from app.ai.llm.client import llm_client

logger = logging.getLogger(__name__)


async def get_conversation_memory(
    db: AsyncSession,
    conversation_id: int,
    user_id: int,
    max_recent_messages: int = 10
) -> Tuple[Conversation, Optional[str], List[ChatMessage]]:
    """
    Retrieves stateful conversation memory:
    1. Validates ownership of conversation session.
    2. Fetches rolling summary if present.
    3. Pulls last `max_recent_messages` messages as active context window.
    """
    stmt = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    result = await db.execute(stmt)
    conv = result.scalar_one_or_none()

    if not conv:
        raise ValueError(f"Conversation #{conversation_id} not found or access denied.")

    # Fetch recent messages
    msg_stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(max_recent_messages)
    )
    msg_result = await db.execute(msg_stmt)
    recent_msgs_reverse = msg_result.scalars().all()

    # Re-order chronologically (oldest to newest)
    recent_msgs = list(reversed(recent_msgs_reverse))

    history_chat_messages: List[ChatMessage] = []
    for m in recent_msgs:
        history_chat_messages.append(ChatMessage(role=m.role, content=m.content))

    return conv, conv.summary, history_chat_messages


async def add_message_to_db(
    db: AsyncSession,
    conversation_id: int,
    role: str,
    content: str,
    tokens: int
) -> Message:
    """
    Persists a chat message in the database for stateful session memory.
    """
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tokens=tokens
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    # Auto-update conversation title if first user message
    if role == "user":
        conv = await db.get(Conversation, conversation_id)
        if conv and conv.title == "New Conversation":
            # Generate 5-word title summary
            short_title = content[:40] + ("..." if len(content) > 40 else "")
            conv.title = short_title
            await db.commit()

    return msg


async def maybe_summarize_conversation(
    db: AsyncSession,
    conversation_id: int,
    threshold: int = 12
):
    """
    Rolling Conversation Summarizer:
    When message history exceeds `threshold`, condenses older messages into a rolling summary
    to prevent LLM context window overflow.
    """
    count_stmt = select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
    count_res = await db.execute(count_stmt)
    total_messages = count_res.scalar() or 0

    if total_messages < threshold:
        return

    # Fetch older messages beyond recent 10
    old_stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(total_messages - 8)
    )
    old_res = await db.execute(old_stmt)
    old_messages = old_res.scalars().all()

    if not old_messages:
        return

    old_text = "\n".join([f"{m.role.upper()}: {m.content}" for m in old_messages])
    conv = await db.get(Conversation, conversation_id)

    prompt = (
        f"EXISTING SUMMARY: {conv.summary or 'None'}\n\n"
        f"OLDER MESSAGES TO SUMMARIZE:\n{old_text}\n\n"
        "Generate a concise 3-sentence rolling summary capturing key facts and user context."
    )

    summary_res = await llm_client.generate_chat_response(
        prompt=prompt,
        system_instruction="You are a conversation summarizer.",
        temperature=0.2
    )

    conv.summary = summary_res.answer.strip()
    await db.commit()
