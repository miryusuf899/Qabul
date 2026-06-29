from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ServiceBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    duration_minutes: int = Field(gt=0, le=24 * 60)
    is_active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    duration_minutes: int | None = Field(default=None, gt=0, le=24 * 60)
    is_active: bool | None = None


class ServiceRead(ServiceBase):
    id: int
    business_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
