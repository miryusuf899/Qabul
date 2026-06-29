from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from app.dependencies import CurrentUser, DbSession
from app.models import WorkingHour
from app.schemas.working_hour import WorkingHourRead, WorkingHourUpsert
from app.utils.permissions import ensure_owner_or_admin

router = APIRouter(tags=["working-hours"])


@router.post("/businesses/{business_id}/working-hours", response_model=list[WorkingHourRead])
async def upsert_working_hours(
    business_id: int,
    payload: list[WorkingHourUpsert],
    db: DbSession,
    current_user: CurrentUser,
) -> list[WorkingHour]:
    await ensure_owner_or_admin(db, business_id, current_user)

    existing_result = await db.execute(
        select(WorkingHour).where(WorkingHour.business_id == business_id)
    )
    existing_by_day = {row.day_of_week: row for row in existing_result.scalars().all()}

    for item in payload:
        working_hour = existing_by_day.get(item.day_of_week)
        values = item.model_dump()
        if working_hour is None:
            db.add(WorkingHour(business_id=business_id, **values))
        else:
            for field, value in values.items():
                setattr(working_hour, field, value)

    await db.commit()
    return await list_working_hours(business_id, db, current_user)


@router.get("/businesses/{business_id}/working-hours", response_model=list[WorkingHourRead])
async def list_working_hours(
    business_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> list[WorkingHour]:
    await ensure_owner_or_admin(db, business_id, current_user)
    result = await db.execute(
        select(WorkingHour)
        .where(WorkingHour.business_id == business_id)
        .order_by(WorkingHour.day_of_week)
    )
    return list(result.scalars().all())
