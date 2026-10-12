
import json
from typing import Any

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    message_to_dict,
    messages_from_dict,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apex_ai.database.chat_history import (
    add_message,
    create_conversation,
    get_messages,
)
from apex_ai.database.models import Conversation


def _message_role(message: Any) -> str:
    if isinstance(message, HumanMessage):
        return "user"
    if isinstance(message, AIMessage):
        return "assistant"
    if isinstance(message, SystemMessage):
        return "system"
    if isinstance(message, ToolMessage):
        return "tool"
    raise ValueError(f"Unsupported message type: {type(message).__name__}")


def _message_content(message: Any) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    return json.dumps(content, ensure_ascii=False, default=str)


def _restore_message(saved_message: Any) -> Any:
    metadata = saved_message.metadata_json

    if metadata and "langchain_message" in metadata:
        return messages_from_dict([metadata["langchain_message"]])[0]

    # Fallback for messages saved before metadata was added.
    if saved_message.role == "user":
        return HumanMessage(content=saved_message.content)
    if saved_message.role == "assistant":
        return AIMessage(content=saved_message.content)
    if saved_message.role == "system":
        return SystemMessage(content=saved_message.content)
    if saved_message.role == "tool":
        return ToolMessage(
            content=saved_message.content,
            tool_call_id="legacy-tool-call",
        )

    raise ValueError(f"Unsupported stored role: {saved_message.role}")


async def _get_owned_conversation(
    db: AsyncSession,
    conversation_id: int,
    user_id: int | None,
) -> Conversation:
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    )

    conversation = await db.scalar(statement)

    if conversation is None:
        raise ValueError("Conversation not found or access denied")

    return conversation


async def get_chat_history(
    db: AsyncSession,
    conversation_id: int,
    user_id: int | None,
) -> list[dict[str, Any]]:
    await _get_owned_conversation(db, conversation_id, user_id)

    saved_messages = await get_messages(db, conversation_id)

    return [
        {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at,
        }
        for message in saved_messages
    ]


async def send_chat_message(
    agent: Any,
    db: AsyncSession,
    user_text: str,
    user_id: int | None = None,
    conversation_id: int | None = None,
) -> dict[str, Any]:
    user_text = user_text.strip()

    if not user_text:
        raise ValueError("Message cannot be empty")

    # Start a new conversation or verify ownership of an existing one.
    if conversation_id is None:
        title = user_text[:60]
        conversation = await create_conversation(
            db,
            user_id=user_id,
            title=title,
        )
        conversation_id = conversation.id
    else:
        await _get_owned_conversation(
            db,
            conversation_id,
            user_id,
        )

    saved_messages = await get_messages(db, conversation_id)
    history = [_restore_message(item) for item in saved_messages]

    current_user_message = HumanMessage(content=user_text)

    await add_message(
        db,
        conversation_id=conversation_id,
        role="user",
        content=user_text,
        metadata_json={
            "langchain_message": message_to_dict(current_user_message)
        },
    )

    history.append(current_user_message)
    input_message_count = len(history)

    try:
        result = await agent.ainvoke({"messages": history})
    except Exception:
        # The user message remains saved, even if the agent fails.
        raise

    result_messages = result.get("messages", [])

    if not result_messages:
        raise RuntimeError("The agent returned no messages")

    # Save new graph messages, including tool-call messages and tool results.
    new_messages = result_messages[input_message_count:]

    for message in new_messages:
        role = _message_role(message)

        await add_message(
            db,
            conversation_id=conversation_id,
            role=role,
            content=_message_content(message),
            metadata_json={
                "langchain_message": message_to_dict(message)
            },
        )

    # If the graph returned a response without appending it to state,
    # save that response explicitly.
    if not new_messages:
        final_message = next(
            (
                message
                for message in reversed(result_messages)
                if isinstance(message, AIMessage)
                and not message.tool_calls
            ),
            None,
        )

        if final_message is None:
            raise RuntimeError("The agent did not return a final response")

        await add_message(
            db,
            conversation_id=conversation_id,
            role="assistant",
            content=_message_content(final_message),
            metadata_json={
                "langchain_message": message_to_dict(final_message)
            },
        )
    else:
        final_message = next(
            (
                message
                for message in reversed(new_messages)
                if isinstance(message, AIMessage)
                and not message.tool_calls
            ),
            None,
        )

        if final_message is None:
            raise RuntimeError("The agent did not return a final response")

    return {
        "conversation_id": conversation_id,
        "reply": _message_content(final_message),
    }
