from __future__ import annotations

from pydantic import BaseModel


class CountItem(BaseModel):
    id: int | None = None
    name: str | None = None
    full_name: str | None = None
    count: int = 0


class DashboardSummary(BaseModel):
    today_bookings: int
    week_bookings: int
    month_bookings: int
    today_revenue: float
    month_revenue: float
    new_clients_this_month: int
    cancelled_bookings_this_month: int
    popular_service: CountItem | None
    top_staff: CountItem | None


class TimeSeriesItem(BaseModel):
    date: str
    value: float


class DashboardCharts(BaseModel):
    bookings_by_day: list[TimeSeriesItem]
    revenue_by_day: list[TimeSeriesItem]
    service_popularity: list[CountItem]
    top_staff: list[CountItem]
