from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClientUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    telegram_username: str | None = Field(default=None, max_length=255)


class ClientRead(BaseModel):
    id: int
    business_id: int
    full_name: str | None
    phone: str | None
    telegram_id: int | None
    telegram_username: str | None
    total_visits: int
    last_visit_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
