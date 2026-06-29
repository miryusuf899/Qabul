from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Booking, BookingStatus, Business, Client, Service, Staff
from app.schemas.dashboard import CountItem, DashboardCharts, DashboardSummary, TimeSeriesItem
from app.services.booking_service import ACTIVE_REVENUE_STATUSES
from app.utils.datetime_utils import combine_local, now_in_timezone


def _range_for_today(business: Business) -> tuple[datetime, datetime]:
    today = now_in_timezone(business.timezone).date()
    return combine_local(today, time.min, business.timezone), combine_local(today, time.max, business.timezone)


def _range_for_month(business: Business) -> tuple[datetime, datetime]:
    now = now_in_timezone(business.timezone)
    start = combine_local(date(now.year, now.month, 1), time.min, business.timezone)
    if now.month == 12:
        next_month = date(now.year + 1, 1, 1)
    else:
        next_month = date(now.year, now.month + 1, 1)
    end = combine_local(next_month, time.min, business.timezone) - timedelta(microseconds=1)
    return start, end


def _range_for_week(business: Business) -> tuple[datetime, datetime]:
    now = now_in_timezone(business.timezone)
    monday = now.date() - timedelta(days=now.weekday())
    start = combine_local(monday, time.min, business.timezone)
    end = start + timedelta(days=7) - timedelta(microseconds=1)
    return start, end


async def _count_bookings(db: AsyncSession, business_id: int, start: datetime, end: datetime) -> int:
    result = await db.execute(
        select(func.count(Booking.id)).where(
            Booking.business_id == business_id,
            Booking.start_time >= start,
            Booking.start_time <= end,
            Booking.status != BookingStatus.CANCELLED,
        )
    )
    return int(result.scalar() or 0)


async def _count_cancelled(db: AsyncSession, business_id: int, start: datetime, end: datetime) -> int:
    result = await db.execute(
        select(func.count(Booking.id)).where(
            Booking.business_id == business_id,
            Booking.start_time >= start,
            Booking.start_time <= end,
            Booking.status == BookingStatus.CANCELLED,
        )
    )
    return int(result.scalar() or 0)


async def _revenue(db: AsyncSession, business_id: int, start: datetime, end: datetime) -> float:
    result = await db.execute(
        select(func.coalesce(func.sum(Service.price), 0))
        .join(Booking, Booking.service_id == Service.id)
        .where(
            Booking.business_id == business_id,
            Booking.start_time >= start,
            Booking.start_time <= end,
            Booking.status.in_(ACTIVE_REVENUE_STATUSES),
        )
    )
    value = result.scalar() or Decimal("0")
    return float(value)


async def get_dashboard_summary(db: AsyncSession, business: Business) -> DashboardSummary:
    today_start, today_end = _range_for_today(business)
    week_start, week_end = _range_for_week(business)
    month_start, month_end = _range_for_month(business)

    new_clients_result = await db.execute(
        select(func.count(Client.id)).where(
            Client.business_id == business.id,
            Client.created_at >= month_start,
            Client.created_at <= month_end,
        )
    )

    popular_result = await db.execute(
        select(Service.id, Service.name, func.count(Booking.id).label("count"))
        .join(Booking, Booking.service_id == Service.id)
        .where(
            Booking.business_id == business.id,
            Booking.start_time >= month_start,
            Booking.start_time <= month_end,
            Booking.status.in_(ACTIVE_REVENUE_STATUSES),
        )
        .group_by(Service.id, Service.name)
        .order_by(func.count(Booking.id).desc())
        .limit(1)
    )
    popular_row = popular_result.first()

    top_staff_result = await db.execute(
        select(Staff.id, Staff.full_name, func.count(Booking.id).label("count"))
        .join(Booking, Booking.staff_id == Staff.id)
        .where(
            Booking.business_id == business.id,
            Booking.start_time >= month_start,
            Booking.start_time <= month_end,
            Booking.status.in_(ACTIVE_REVENUE_STATUSES),
        )
        .group_by(Staff.id, Staff.full_name)
        .order_by(func.count(Booking.id).desc())
        .limit(1)
    )
    top_staff_row = top_staff_result.first()

    return DashboardSummary(
        today_bookings=await _count_bookings(db, business.id, today_start, today_end),
        week_bookings=await _count_bookings(db, business.id, week_start, week_end),
        month_bookings=await _count_bookings(db, business.id, month_start, month_end),
        today_revenue=await _revenue(db, business.id, today_start, today_end),
        month_revenue=await _revenue(db, business.id, month_start, month_end),
        new_clients_this_month=int(new_clients_result.scalar() or 0),
        cancelled_bookings_this_month=await _count_cancelled(db, business.id, month_start, month_end),
        popular_service=(
            CountItem(id=popular_row.id, name=popular_row.name, count=popular_row.count)
            if popular_row
            else None
        ),
        top_staff=(
            CountItem(id=top_staff_row.id, full_name=top_staff_row.full_name, count=top_staff_row.count)
            if top_staff_row
            else None
        ),
    )


def _normalize_day(value: object) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


async def get_dashboard_charts(db: AsyncSession, business: Business) -> DashboardCharts:
    today = now_in_timezone(business.timezone).date()
    start_day = today - timedelta(days=13)
    start = combine_local(start_day, time.min, business.timezone)
    end = combine_local(today, time.max, business.timezone)
    labels = [(start_day + timedelta(days=index)).isoformat() for index in range(14)]

    bookings_result = await db.execute(
        select(func.date(Booking.start_time), func.count(Booking.id))
        .where(
            Booking.business_id == business.id,
            Booking.start_time >= start,
            Booking.start_time <= end,
            Booking.status != BookingStatus.CANCELLED,
        )
        .group_by(func.date(Booking.start_time))
        .order_by(func.date(Booking.start_time))
    )
    bookings_by_day = {label: 0 for label in labels}
    for day_value, count in bookings_result.all():
        bookings_by_day[_normalize_day(day_value)] = int(count)

    revenue_result = await db.execute(
        select(func.date(Booking.start_time), func.coalesce(func.sum(Service.price), 0))
        .join(Service, Service.id == Booking.service_id)
        .where(
            Booking.business_id == business.id,
            Booking.start_time >= start,
            Booking.start_time <= end,
            Booking.status.in_(ACTIVE_REVENUE_STATUSES),
        )
        .group_by(func.date(Booking.start_time))
        .order_by(func.date(Booking.start_time))
    )
    revenue_by_day = {label: 0.0 for label in labels}
    for day_value, value in revenue_result.all():
        revenue_by_day[_normalize_day(day_value)] = float(value or 0)

    service_result = await db.execute(
        select(Service.id, Service.name, func.count(Booking.id).label("count"))
        .join(Booking, Booking.service_id == Service.id)
        .where(Booking.business_id == business.id, Booking.status.in_(ACTIVE_REVENUE_STATUSES))
        .group_by(Service.id, Service.name)
        .order_by(func.count(Booking.id).desc())
        .limit(10)
    )

    staff_result = await db.execute(
        select(Staff.id, Staff.full_name, func.count(Booking.id).label("count"))
        .join(Booking, Booking.staff_id == Staff.id)
        .where(Booking.business_id == business.id, Booking.status.in_(ACTIVE_REVENUE_STATUSES))
        .group_by(Staff.id, Staff.full_name)
        .order_by(func.count(Booking.id).desc())
        .limit(10)
    )

    return DashboardCharts(
        bookings_by_day=[TimeSeriesItem(date=label, value=value) for label, value in bookings_by_day.items()],
        revenue_by_day=[TimeSeriesItem(date=label, value=value) for label, value in revenue_by_day.items()],
        service_popularity=[
            CountItem(id=row.id, name=row.name, count=row.count) for row in service_result.all()
        ],
        top_staff=[
            CountItem(id=row.id, full_name=row.full_name, count=row.count) for row in staff_result.all()
        ],
    )
