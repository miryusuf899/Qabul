from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class StaffBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    specialization: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class StaffCreate(StaffBase):
    service_ids: list[int] = Field(default_factory=list)


class StaffUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    specialization: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class StaffServicesUpdate(BaseModel):
    service_ids: list[int] = Field(default_factory=list)


class StaffRead(StaffBase):
    id: int
    business_id: int
    service_ids: list[int] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
