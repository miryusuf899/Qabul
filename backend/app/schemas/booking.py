from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import BookingSource, BookingStatus


class BookingCreate(BaseModel):
    client_name: str | None = Field(default=None, max_length=255)
    client_phone: str | None = Field(default=None, max_length=32)
    telegram_id: int | None = None
    telegram_username: str | None = Field(default=None, max_length=255)
    staff_id: int
    service_id: int
    start_time: datetime
    note: str | None = None


class BookingUpdate(BaseModel):
    client_name: str | None = Field(default=None, max_length=255)
    client_phone: str | None = Field(default=None, max_length=32)
    staff_id: int | None = None
    service_id: int | None = None
    start_time: datetime | None = None
    note: str | None = None


class BookingStatusUpdate(BaseModel):
    status: BookingStatus
    cancel_reason: str | None = None


class BookingRead(BaseModel):
    id: int
    business_id: int
    client_id: int
    client_name: str | None
    client_phone: str | None
    telegram_id: int | None
    staff_id: int
    staff_name: str
    service_id: int
    service_name: str
    service_price: float
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    source: BookingSource
    note: str | None
    cancel_reason: str | None
    created_at: datetime
    updated_at: datetime


class AvailableSlotsResponse(BaseModel):
    slots: list[str]
