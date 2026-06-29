from __future__ import annotations

from pydantic import BaseModel, Field


class AIChatRequest(BaseModel):
    business_id: int
    telegram_id: int | None = None
    telegram_username: str | None = Field(default=None, max_length=255)
    client_name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    message: str = Field(min_length=1, max_length=2000)


class AIChatResponse(BaseModel):
    reply: str
    intent: str
    action_taken: str | None = None
