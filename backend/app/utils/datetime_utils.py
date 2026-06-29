from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from app.config import settings


def get_timezone(name: str | None = None) -> ZoneInfo:
    return ZoneInfo(name or settings.timezone)


def ensure_aware(value: datetime, timezone_name: str | None = None) -> datetime:
    if value.tzinfo is not None and value.utcoffset() is not None:
        return value
    return value.replace(tzinfo=get_timezone(timezone_name))


def now_in_timezone(timezone_name: str | None = None) -> datetime:
    return datetime.now(get_timezone(timezone_name))


def combine_local(day: date, value: time, timezone_name: str | None = None) -> datetime:
    return datetime.combine(day, value, tzinfo=get_timezone(timezone_name))


def day_bounds(day: date, timezone_name: str | None = None) -> tuple[datetime, datetime]:
    start = combine_local(day, time.min, timezone_name)
    end = combine_local(day, time.max, timezone_name)
    return start, end
