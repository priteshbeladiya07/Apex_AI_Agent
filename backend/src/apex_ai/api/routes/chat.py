from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from apex_ai.database.session import get_db
from apex_ai.schemas.chat import (
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
)
from apex_ai.services.conversation_service import (
    get_chat_history,
    send_chat_message,
)
from apex_ai.core.logging import get_logger

router = APIRouter()
logger = get_logger("api.chat")


@router.post("/", response_model=ChatResponse)
async def send_message(
    payload: ChatRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    agent = getattr(request.app.state, "agent", None)

    if agent is None:
        raise HTTPException(
            status_code=503,
            detail="AI agent has not been initialized",
        )

    try:
        result = await send_chat_message(
            agent=agent,
            db=db,
            user_text=payload.message,
            user_id=None,
            conversation_id=payload.conversation_id,
        )
        return ChatResponse(**result)

    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    except Exception as exc:
        logger.exception("Failed to process chat request")
        raise HTTPException(
            status_code=500,
            detail="Failed to process chat request; check the backend logs",
        ) from exc


@router.get(
    "/{conversation_id}/history",
    response_model=ChatHistoryResponse,
)
async def chat_history(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        messages = await get_chat_history(
            db=db,
            conversation_id=conversation_id,
            user_id=None,
        )

        return ChatHistoryResponse(
            conversation_id=conversation_id,
            messages=messages,
        )

    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc