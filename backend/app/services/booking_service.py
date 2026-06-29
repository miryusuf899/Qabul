from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Booking,
    BookingSource,
    BookingStatus,
    Business,
    Client,
    Service,
    Staff,
    StaffService,
    WorkingHour,
)
from app.schemas.booking import BookingCreate, BookingRead, BookingUpdate
from app.utils.datetime_utils import combine_local, ensure_aware, get_timezone, now_in_timezone
from app.utils.exceptions import bad_request, not_found

BLOCKING_STATUSES = (BookingStatus.PENDING, BookingStatus.CONFIRMED)
ACTIVE_REVENUE_STATUSES = (BookingStatus.CONFIRMED, BookingStatus.COMPLETED)


def _booking_load_options() -> tuple:
    return (
        selectinload(Booking.client),
        selectinload(Booking.staff),
        selectinload(Booking.service),
    )


def booking_to_read(booking: Booking) -> BookingRead:
    return BookingRead(
        id=booking.id,
        business_id=booking.business_id,
        client_id=booking.client_id,
        client_name=booking.client.full_name,
        client_phone=booking.client.phone,
        telegram_id=booking.client.telegram_id,
        staff_id=booking.staff_id,
        staff_name=booking.staff.full_name,
        service_id=booking.service_id,
        service_name=booking.service.name,
        service_price=float(booking.service.price),
        start_time=booking.start_time,
        end_time=booking.end_time,
        status=booking.status,
        source=booking.source,
        note=booking.note,
        cancel_reason=booking.cancel_reason,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )


async def load_booking(db: AsyncSession, booking_id: int) -> Booking:
    result = await db.execute(
        select(Booking)
        .options(*_booking_load_options())
        .where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()
    if booking is None:
        raise not_found("Booking not found")
    return booking


async def find_or_create_client(
    db: AsyncSession,
    business_id: int,
    phone: str | None = None,
    telegram_id: int | None = None,
    full_name: str | None = None,
    telegram_username: str | None = None,
) -> Client:
    client: Client | None = None
    if telegram_id is not None:
        result = await db.execute(
            select(Client).where(Client.business_id == business_id, Client.telegram_id == telegram_id)
        )
        client = result.scalar_one_or_none()
    if client is None and phone:
        result = await db.execute(
            select(Client).where(Client.business_id == business_id, Client.phone == phone)
        )
        client = result.scalar_one_or_none()

    if client is None:
        client = Client(
            business_id=business_id,
            full_name=full_name,
            phone=phone,
            telegram_id=telegram_id,
            telegram_username=telegram_username,
        )
        db.add(client)
        await db.flush()
        return client

    if full_name and not client.full_name:
        client.full_name = full_name
    if phone and not client.phone:
        client.phone = phone
    if telegram_username and not client.telegram_username:
        client.telegram_username = telegram_username
    await db.flush()
    return client


async def _get_active_business(db: AsyncSession, business_id: int) -> Business:
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    if business is None or not business.is_active:
        raise not_found("Business not found")
    return business


async def _get_active_service(db: AsyncSession, business_id: int, service_id: int) -> Service:
    result = await db.execute(
        select(Service).where(
            Service.id == service_id,
            Service.business_id == business_id,
            Service.is_active.is_(True),
        )
    )
    service = result.scalar_one_or_none()
    if service is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Service is not available")
    return service


async def _get_active_staff(db: AsyncSession, business_id: int, staff_id: int) -> Staff:
    result = await db.execute(
        select(Staff).where(
            Staff.id == staff_id,
            Staff.business_id == business_id,
            Staff.is_active.is_(True),
        )
    )
    staff = result.scalar_one_or_none()
    if staff is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Staff is not available")
    return staff


async def _ensure_staff_can_do_service(db: AsyncSession, staff_id: int, service_id: int) -> None:
    result = await db.execute(
        select(StaffService).where(
            StaffService.staff_id == staff_id,
            StaffService.service_id == service_id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Staff cannot perform this service",
        )


async def check_business_working_time(
    db: AsyncSession,
    business_id: int,
    start_time: datetime,
    end_time: datetime,
) -> None:
    business = await _get_active_business(db, business_id)
    timezone = get_timezone(business.timezone)
    start_local = ensure_aware(start_time, business.timezone).astimezone(timezone)
    end_local = ensure_aware(end_time, business.timezone).astimezone(timezone)

    if start_local <= now_in_timezone(business.timezone):
        raise bad_request("Cannot create booking in the past")
    if start_local.date() != end_local.date():
        raise bad_request("Booking must fit into one working day")

    result = await db.execute(
        select(WorkingHour).where(
            WorkingHour.business_id == business_id,
            WorkingHour.day_of_week == start_local.weekday(),
        )
    )
    working_hour = result.scalar_one_or_none()
    if working_hour is None or working_hour.is_closed:
        raise bad_request("Business is closed at this time")
    if working_hour.open_time is None or working_hour.close_time is None:
        raise bad_request("Business working hours are not configured")
    if start_local.time() < working_hour.open_time or end_local.time() > working_hour.close_time:
        raise bad_request("Booking is outside working hours")


async def check_staff_available(
    db: AsyncSession,
    staff_id: int,
    start_time: datetime,
    end_time: datetime,
    ignore_booking_id: int | None = None,
) -> None:
    conditions = [
        Booking.staff_id == staff_id,
        Booking.status.in_(BLOCKING_STATUSES),
        Booking.start_time < end_time,
        Booking.end_time > start_time,
    ]
    if ignore_booking_id is not None:
        conditions.append(Booking.id != ignore_booking_id)

    result = await db.execute(select(Booking.id).where(and_(*conditions)).limit(1))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This time slot is already booked",
        )


async def create_booking(
    db: AsyncSession,
    business_id: int,
    payload: BookingCreate,
    source: BookingSource = BookingSource.DASHBOARD,
) -> Booking:
    business = await _get_active_business(db, business_id)
    service = await _get_active_service(db, business_id, payload.service_id)
    await _get_active_staff(db, business_id, payload.staff_id)
    await _ensure_staff_can_do_service(db, payload.staff_id, payload.service_id)

    start_time = ensure_aware(payload.start_time, business.timezone)
    end_time = start_time + timedelta(minutes=service.duration_minutes)

    await check_business_working_time(db, business_id, start_time, end_time)
    await check_staff_available(db, payload.staff_id, start_time, end_time)

    client = await find_or_create_client(
        db,
        business_id,
        phone=payload.client_phone,
        telegram_id=payload.telegram_id,
        full_name=payload.client_name,
        telegram_username=payload.telegram_username,
    )
    booking = Booking(
        business_id=business_id,
        client_id=client.id,
        staff_id=payload.staff_id,
        service_id=payload.service_id,
        start_time=start_time,
        end_time=end_time,
        status=BookingStatus.CONFIRMED,
        source=source,
        note=payload.note,
    )
    db.add(booking)
    await db.commit()
    return await load_booking(db, booking.id)


async def cancel_booking(db: AsyncSession, booking_id: int, reason: str | None = None) -> Booking:
    booking = await load_booking(db, booking_id)
    booking.status = BookingStatus.CANCELLED
    booking.cancel_reason = reason
    await db.commit()
    return await load_booking(db, booking_id)


async def reschedule_booking(
    db: AsyncSession,
    booking_id: int,
    new_start_time: datetime,
) -> Booking:
    booking = await load_booking(db, booking_id)
    business = await _get_active_business(db, booking.business_id)
    service = await _get_active_service(db, booking.business_id, booking.service_id)
    start_time = ensure_aware(new_start_time, business.timezone)
    end_time = start_time + timedelta(minutes=service.duration_minutes)

    await check_business_working_time(db, booking.business_id, start_time, end_time)
    await check_staff_available(db, booking.staff_id, start_time, end_time, ignore_booking_id=booking_id)

    booking.start_time = start_time
    booking.end_time = end_time
    await db.commit()
    return await load_booking(db, booking_id)


async def update_booking(db: AsyncSession, booking_id: int, payload: BookingUpdate) -> Booking:
    booking = await load_booking(db, booking_id)
    business = await _get_active_business(db, booking.business_id)

    if payload.client_name is not None:
        booking.client.full_name = payload.client_name
    if payload.client_phone is not None:
        booking.client.phone = payload.client_phone
    if payload.note is not None:
        booking.note = payload.note

    staff_id = payload.staff_id or booking.staff_id
    service_id = payload.service_id or booking.service_id
    service = await _get_active_service(db, booking.business_id, service_id)
    await _get_active_staff(db, booking.business_id, staff_id)
    await _ensure_staff_can_do_service(db, staff_id, service_id)

    start_time = ensure_aware(payload.start_time or booking.start_time, business.timezone)
    end_time = start_time + timedelta(minutes=service.duration_minutes)
    await check_business_working_time(db, booking.business_id, start_time, end_time)
    await check_staff_available(db, staff_id, start_time, end_time, ignore_booking_id=booking_id)

    booking.staff_id = staff_id
    booking.service_id = service_id
    booking.start_time = start_time
    booking.end_time = end_time
    await db.commit()
    return await load_booking(db, booking_id)


async def change_booking_status(
    db: AsyncSession,
    booking_id: int,
    status_value: BookingStatus,
    cancel_reason: str | None = None,
) -> Booking:
    booking = await load_booking(db, booking_id)
    old_status = booking.status
    booking.status = status_value
    if status_value == BookingStatus.CANCELLED:
        booking.cancel_reason = cancel_reason
    if status_value == BookingStatus.COMPLETED and old_status != BookingStatus.COMPLETED:
        booking.client.total_visits += 1
        booking.client.last_visit_at = booking.end_time
    await db.commit()
    return await load_booking(db, booking_id)


def _slot_is_available(
    bookings: Iterable[Booking],
    start_time: datetime,
    end_time: datetime,
    timezone_name: str,
) -> bool:
    for booking in bookings:
        existing_start = ensure_aware(booking.start_time, timezone_name)
        existing_end = ensure_aware(booking.end_time, timezone_name)
        if start_time < existing_end and end_time > existing_start:
            return False
    return True


async def _candidate_staff_for_service(
    db: AsyncSession,
    business_id: int,
    service_id: int,
    staff_id: int | None = None,
) -> list[Staff]:
    query = (
        select(Staff)
        .join(StaffService, StaffService.staff_id == Staff.id)
        .where(
            Staff.business_id == business_id,
            Staff.is_active.is_(True),
            StaffService.service_id == service_id,
        )
        .order_by(Staff.id)
    )
    if staff_id is not None:
        query = query.where(Staff.id == staff_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_available_slots(
    db: AsyncSession,
    business_id: int,
    service_id: int,
    slot_date: date,
    staff_id: int | None = None,
) -> list[str]:
    business = await _get_active_business(db, business_id)
    service = await _get_active_service(db, business_id, service_id)
    candidates = await _candidate_staff_for_service(db, business_id, service_id, staff_id)
    if not candidates:
        return []

    result = await db.execute(
        select(WorkingHour).where(
            WorkingHour.business_id == business_id,
            WorkingHour.day_of_week == slot_date.weekday(),
        )
    )
    working_hour = result.scalar_one_or_none()
    if working_hour is None or working_hour.is_closed or not working_hour.open_time or not working_hour.close_time:
        return []

    day_start = combine_local(slot_date, working_hour.open_time, business.timezone)
    day_end = combine_local(slot_date, working_hour.close_time, business.timezone)
    latest_start = day_end - timedelta(minutes=service.duration_minutes)
    if latest_start < day_start:
        return []

    staff_ids = [staff.id for staff in candidates]
    bookings_result = await db.execute(
        select(Booking).where(
            Booking.staff_id.in_(staff_ids),
            Booking.status.in_(BLOCKING_STATUSES),
            Booking.start_time < day_end,
            Booking.end_time > day_start,
        )
    )
    bookings_by_staff: dict[int, list[Booking]] = {staff.id: [] for staff in candidates}
    for booking in bookings_result.scalars().all():
        bookings_by_staff.setdefault(booking.staff_id, []).append(booking)

    now = now_in_timezone(business.timezone)
    slots: list[str] = []
    current = day_start
    step = timedelta(minutes=30)
    while current <= latest_start:
        slot_end = current + timedelta(minutes=service.duration_minutes)
        if current > now:
            for candidate in candidates:
                if _slot_is_available(
                    bookings_by_staff.get(candidate.id, []),
                    current,
                    slot_end,
                    business.timezone,
                ):
                    slots.append(current.strftime("%H:%M"))
                    break
        current += step
    return slots


def apply_booking_filters(
    query: Select[tuple[Booking]],
    status_value: BookingStatus | None = None,
    staff_id: int | None = None,
    service_id: int | None = None,
    start_from: datetime | None = None,
    start_to: datetime | None = None,
) -> Select[tuple[Booking]]:
    if status_value is not None:
        query = query.where(Booking.status == status_value)
    if staff_id is not None:
        query = query.where(Booking.staff_id == staff_id)
    if service_id is not None:
        query = query.where(Booking.service_id == service_id)
    if start_from is not None:
        query = query.where(Booking.start_time >= start_from)
    if start_to is not None:
        query = query.where(Booking.start_time <= start_to)
    return query
