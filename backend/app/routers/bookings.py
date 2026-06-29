from __future__ import annotations

from datetime import date, time

from fastapi import APIRouter, Query, status
from sqlalchemy import select

from app.dependencies import CurrentUser, DbSession
from app.models import Booking, BookingStatus
from app.schemas.booking import (
    AvailableSlotsResponse,
    BookingCreate,
    BookingRead,
    BookingStatusUpdate,
    BookingUpdate,
)
from app.services.booking_service import (
    apply_booking_filters,
    booking_to_read,
    cancel_booking,
    change_booking_status,
    create_booking,
    get_available_slots,
    load_booking,
    update_booking,
)
from app.utils.datetime_utils import combine_local
from app.utils.permissions import ensure_owner_or_admin

router = APIRouter(tags=["bookings"])


@router.post("/businesses/{business_id}/bookings", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking_endpoint(
    business_id: int,
    payload: BookingCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> BookingRead:
    await ensure_owner_or_admin(db, business_id, current_user)
    booking = await create_booking(db, business_id, payload)
    return booking_to_read(booking)


@router.get("/businesses/{business_id}/bookings", response_model=list[BookingRead])
async def list_bookings(
    business_id: int,
    db: DbSession,
    current_user: CurrentUser,
    date_filter: date | None = Query(default=None, alias="date"),
    status_filter: BookingStatus | None = Query(default=None, alias="status"),
    staff_id: int | None = None,
    service_id: int | None = None,
) -> list[BookingRead]:
    business = await ensure_owner_or_admin(db, business_id, current_user)
    start_from = start_to = None
    if date_filter is not None:
        start_from = combine_local(date_filter, time.min, business.timezone)
        start_to = combine_local(date_filter, time.max, business.timezone)

    query = select(Booking).where(Booking.business_id == business_id).order_by(Booking.start_time)
    query = query.options(*load_booking_options())
    query = apply_booking_filters(
        query,
        status_value=status_filter,
        staff_id=staff_id,
        service_id=service_id,
        start_from=start_from,
        start_to=start_to,
    )
    result = await db.execute(query)
    return [booking_to_read(booking) for booking in result.scalars().all()]


@router.get("/businesses/{business_id}/bookings/available-slots", response_model=AvailableSlotsResponse)
async def available_slots(
    business_id: int,
    db: DbSession,
    current_user: CurrentUser,
    service_id: int = Query(...),
    slot_date: date = Query(alias="date"),
    staff_id: int | None = None,
) -> AvailableSlotsResponse:
    await ensure_owner_or_admin(db, business_id, current_user)
    slots = await get_available_slots(db, business_id, service_id, slot_date, staff_id=staff_id)
    return AvailableSlotsResponse(slots=slots)


@router.get("/bookings/{booking_id}", response_model=BookingRead)
async def get_booking(booking_id: int, db: DbSession, current_user: CurrentUser) -> BookingRead:
    booking = await load_booking(db, booking_id)
    await ensure_owner_or_admin(db, booking.business_id, current_user)
    return booking_to_read(booking)


@router.put("/bookings/{booking_id}", response_model=BookingRead)
async def update_booking_endpoint(
    booking_id: int,
    payload: BookingUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> BookingRead:
    booking = await load_booking(db, booking_id)
    await ensure_owner_or_admin(db, booking.business_id, current_user)
    updated_booking = await update_booking(db, booking_id, payload)
    return booking_to_read(updated_booking)


@router.patch("/bookings/{booking_id}/status", response_model=BookingRead)
async def update_booking_status(
    booking_id: int,
    payload: BookingStatusUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> BookingRead:
    booking = await load_booking(db, booking_id)
    await ensure_owner_or_admin(db, booking.business_id, current_user)
    updated_booking = await change_booking_status(db, booking_id, payload.status, payload.cancel_reason)
    return booking_to_read(updated_booking)


@router.delete("/bookings/{booking_id}", response_model=BookingRead)
async def delete_booking(
    booking_id: int,
    db: DbSession,
    current_user: CurrentUser,
    reason: str | None = None,
) -> BookingRead:
    booking = await load_booking(db, booking_id)
    await ensure_owner_or_admin(db, booking.business_id, current_user)
    cancelled = await cancel_booking(db, booking_id, reason)
    return booking_to_read(cancelled)


def load_booking_options() -> tuple:
    from sqlalchemy.orm import selectinload

    return (
        selectinload(Booking.client),
        selectinload(Booking.staff),
        selectinload(Booking.service),
    )
