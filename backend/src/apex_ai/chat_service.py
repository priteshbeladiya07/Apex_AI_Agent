import json

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from apex_ai.database.chat_history import add_message, get_messages
from apex_ai.database.session import AsyncSessionLocal


async def run_chat_turn(agent, conversation_id: int, user_text: str) -> str:
    async with AsyncSessionLocal() as db:
        saved_messages = await get_messages(db, conversation_id)

        history = []

        for message in saved_messages:
            if message.role == "user":
                history.append(HumanMessage(content=message.content))
            elif message.role == "assistant":
                history.append(AIMessage(content=message.content))
            elif message.role == "system":
                history.append(SystemMessage(content=message.content))

        await add_message(
            db,
            conversation_id=conversation_id,
            role="user",
            content=user_text,
        )

    history.append(HumanMessage(content=user_text))

    result = await agent.ainvoke({"messages": history})

    messages = result.get("messages", [])
    final_message = next(
        (
            message
            for message in reversed(messages)
            if isinstance(message, AIMessage)
        ),
        None,
    )

    if final_message is None:
        raise RuntimeError("The agent did not return an assistant response")

    content = final_message.content
    answer = (
        content
        if isinstance(content, str)
        else json.dumps(content, ensure_ascii=False, default=str)
    )

    async with AsyncSessionLocal() as db:
        await add_message(
            db,
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
        )

    return answer