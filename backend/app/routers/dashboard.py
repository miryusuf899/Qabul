from __future__ import annotations

from fastapi import APIRouter

from app.dependencies import CurrentUser, DbSession
from app.schemas.dashboard import DashboardCharts, DashboardSummary
from app.services.dashboard_service import get_dashboard_charts, get_dashboard_summary
from app.utils.permissions import ensure_owner_or_admin

router = APIRouter(tags=["dashboard"])


@router.get("/businesses/{business_id}/dashboard/summary", response_model=DashboardSummary)
async def dashboard_summary(
    business_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> DashboardSummary:
    business = await ensure_owner_or_admin(db, business_id, current_user)
    return await get_dashboard_summary(db, business)


@router.get("/businesses/{business_id}/dashboard/charts", response_model=DashboardCharts)
async def dashboard_charts(
    business_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> DashboardCharts:
    business = await ensure_owner_or_admin(db, business_id, current_user)
    return await get_dashboard_charts(db, business)
