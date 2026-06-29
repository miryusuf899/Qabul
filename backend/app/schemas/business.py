from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BusinessBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    business_type: str = Field(min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=32)
    address: str | None = Field(default=None, max_length=500)
    logo_url: str | None = Field(default=None, max_length=1000)
    timezone: str = Field(default="Asia/Dushanbe", max_length=64)
    ai_enabled: bool = True


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    business_type: str | None = Field(default=None, min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=32)
    address: str | None = Field(default=None, max_length=500)
    logo_url: str | None = Field(default=None, max_length=1000)
    timezone: str | None = Field(default=None, max_length=64)
    ai_enabled: bool | None = None


class BusinessRead(BusinessBase):
    id: int
    owner_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
