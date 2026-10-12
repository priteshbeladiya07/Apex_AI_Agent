from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apex_ai.database.chat_history import get_conversations
from apex_ai.database.models import Conversation
from apex_ai.database.session import get_db
from apex_ai.schemas.chat import ConversationResponse

router = APIRouter()


@router.get("/", response_model=list[ConversationResponse])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
):
    return await get_conversations(db)


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
) -> Response:
    conversation = await db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id.is_(None),
        )
    )

    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await db.delete(conversation)
    await db.commit()
    return Response(status_code=204)
