from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apex_ai.database.models import (
    Conversation,
    Message,
    ToolExecution,
)


async def create_conversation(
    db: AsyncSession,
    user_id: int | None = None,
    title: str = "New chat",
) -> Conversation:
    conversation = Conversation(
        user_id=user_id,
        title=title,
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def add_message(
    db: AsyncSession,
    conversation_id: int,
    role: str,
    content: str,
    metadata_json: dict[str, Any] | None = None,
) -> Message:
    if role not in {"system", "user", "assistant", "tool"}:
        raise ValueError(f"Invalid message role: {role}")

    conversation = await db.get(Conversation, conversation_id)

    if conversation is None:
        raise ValueError("Conversation not found")

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        metadata_json=metadata_json,
    )

    conversation.updated_at = datetime.now(timezone.utc)

    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_messages(
    db: AsyncSession,
    conversation_id: int,
) -> list[Message]:
    result = await db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.id.asc())
    )
    return list(result.all())


async def get_conversations(
    db: AsyncSession,
    user_id: int | None = None,
) -> list[Conversation]:
    result = await db.scalars(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    return list(result.all())


async def record_tool_execution(
    db: AsyncSession,
    conversation_id: int,
    server_name: str,
    tool_name: str,
    arguments: dict[str, Any],
    result: Any = None,
    status: str = "success",
    error: str | None = None,
    message_id: int | None = None,
    duration_ms: int | None = None,
) -> ToolExecution:
    if status not in {"success", "failed"}:
        raise ValueError("Status must be 'success' or 'failed'")

    execution = ToolExecution(
        conversation_id=conversation_id,
        message_id=message_id,
        server_name=server_name,
        tool_name=tool_name,
        arguments=arguments,
        result=result,
        status=status,
        error=error,
        duration_ms=duration_ms,
    )

    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    return execution