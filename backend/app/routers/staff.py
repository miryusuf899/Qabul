from __future__ import annotations

from fastapi import APIRouter, status
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.dependencies import CurrentUser, DbSession
from app.models import Service, Staff, StaffService
from app.schemas.staff import StaffCreate, StaffRead, StaffServicesUpdate, StaffUpdate
from app.utils.exceptions import bad_request, not_found
from app.utils.permissions import ensure_owner_or_admin

router = APIRouter(tags=["staff"])


def staff_to_read(staff: Staff) -> StaffRead:
    return StaffRead(
        id=staff.id,
        business_id=staff.business_id,
        full_name=staff.full_name,
        phone=staff.phone,
        specialization=staff.specialization,
        is_active=staff.is_active,
        service_ids=[link.service_id for link in staff.service_links],
        created_at=staff.created_at,
        updated_at=staff.updated_at,
    )


async def get_staff_for_user(db: DbSession, staff_id: int, current_user: CurrentUser) -> Staff:
    result = await db.execute(
        select(Staff)
        .options(selectinload(Staff.service_links))
        .where(Staff.id == staff_id)
    )
    staff = result.scalar_one_or_none()
    if staff is None:
        raise not_found("Staff not found")
    await ensure_owner_or_admin(db, staff.business_id, current_user)
    return staff


async def validate_service_ids(db: DbSession, business_id: int, service_ids: list[int]) -> list[Service]:
    if not service_ids:
        return []
    unique_ids = sorted(set(service_ids))
    result = await db.execute(
        select(Service).where(Service.id.in_(unique_ids), Service.business_id == business_id)
    )
    services = list(result.scalars().all())
    if len(services) != len(unique_ids):
        raise bad_request("All services must belong to the same business")
    return services


async def replace_staff_services(db: DbSession, staff: Staff, service_ids: list[int]) -> None:
    await validate_service_ids(db, staff.business_id, service_ids)
    await db.execute(delete(StaffService).where(StaffService.staff_id == staff.id))
    for service_id in sorted(set(service_ids)):
        db.add(StaffService(staff_id=staff.id, service_id=service_id))
    await db.flush()


@router.post("/businesses/{business_id}/staff", response_model=StaffRead, status_code=status.HTTP_201_CREATED)
async def create_staff(
    business_id: int,
    payload: StaffCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> StaffRead:
    await ensure_owner_or_admin(db, business_id, current_user)
    await validate_service_ids(db, business_id, payload.service_ids)
    staff = Staff(
        business_id=business_id,
        full_name=payload.full_name,
        phone=payload.phone,
        specialization=payload.specialization,
        is_active=payload.is_active,
    )
    db.add(staff)
    await db.flush()
    for service_id in sorted(set(payload.service_ids)):
        db.add(StaffService(staff_id=staff.id, service_id=service_id))
    await db.commit()
    return await get_staff(staff.id, db, current_user)


@router.get("/businesses/{business_id}/staff", response_model=list[StaffRead])
async def list_staff(business_id: int, db: DbSession, current_user: CurrentUser) -> list[StaffRead]:
    await ensure_owner_or_admin(db, business_id, current_user)
    result = await db.execute(
        select(Staff)
        .options(selectinload(Staff.service_links))
        .where(Staff.business_id == business_id)
        .order_by(Staff.id)
    )
    return [staff_to_read(staff) for staff in result.scalars().all()]


@router.get("/staff/{staff_id}", response_model=StaffRead)
async def get_staff(staff_id: int, db: DbSession, current_user: CurrentUser) -> StaffRead:
    staff = await get_staff_for_user(db, staff_id, current_user)
    return staff_to_read(staff)


@router.put("/staff/{staff_id}", response_model=StaffRead)
async def update_staff(
    staff_id: int,
    payload: StaffUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> StaffRead:
    staff = await get_staff_for_user(db, staff_id, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(staff, field, value)
    await db.commit()
    return await get_staff(staff_id, db, current_user)


@router.delete("/staff/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff(staff_id: int, db: DbSession, current_user: CurrentUser) -> None:
    staff = await get_staff_for_user(db, staff_id, current_user)
    staff.is_active = False
    await db.commit()


@router.post("/staff/{staff_id}/services", response_model=StaffRead)
async def update_staff_services(
    staff_id: int,
    payload: StaffServicesUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> StaffRead:
    staff = await get_staff_for_user(db, staff_id, current_user)
    await replace_staff_services(db, staff, payload.service_ids)
    await db.commit()
    return await get_staff(staff_id, db, current_user)
