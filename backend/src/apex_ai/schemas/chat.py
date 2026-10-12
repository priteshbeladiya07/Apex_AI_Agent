
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRequest(BaseModel):
    conversation_id: int | None = Field(default=None, gt=0)
    message: str = Field(min_length=1, max_length=20000)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Message cannot be empty")

        return value


class ChatResponse(BaseModel):
    conversation_id: int
    reply: str


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    created_at: datetime


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime
    updated_at: datetime


class ChatHistoryResponse(BaseModel):
    conversation_id: int
    messages: list[MessageResponse]
