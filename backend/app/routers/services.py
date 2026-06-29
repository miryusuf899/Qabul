from __future__ import annotations

from fastapi import APIRouter, status
from sqlalchemy import select

from app.dependencies import CurrentUser, DbSession
from app.models import Service
from app.schemas.service import ServiceCreate, ServiceRead, ServiceUpdate
from app.utils.exceptions import not_found
from app.utils.permissions import ensure_owner_or_admin

router = APIRouter(tags=["services"])


async def get_service_for_user(db: DbSession, service_id: int, current_user: CurrentUser) -> Service:
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if service is None:
        raise not_found("Service not found")
    await ensure_owner_or_admin(db, service.business_id, current_user)
    return service


@router.post("/businesses/{business_id}/services", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
async def create_service(
    business_id: int,
    payload: ServiceCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Service:
    await ensure_owner_or_admin(db, business_id, current_user)
    service = Service(business_id=business_id, **payload.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


@router.get("/businesses/{business_id}/services", response_model=list[ServiceRead])
async def list_services(business_id: int, db: DbSession, current_user: CurrentUser) -> list[Service]:
    await ensure_owner_or_admin(db, business_id, current_user)
    result = await db.execute(
        select(Service).where(Service.business_id == business_id).order_by(Service.id)
    )
    return list(result.scalars().all())


@router.put("/services/{service_id}", response_model=ServiceRead)
async def update_service(
    service_id: int,
    payload: ServiceUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> Service:
    service = await get_service_for_user(db, service_id, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(service, field, value)
    await db.commit()
    await db.refresh(service)
    return service


@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(service_id: int, db: DbSession, current_user: CurrentUser) -> None:
    service = await get_service_for_user(db, service_id, current_user)
    service.is_active = False
    await db.commit()
