from __future__ import annotations

from fastapi import APIRouter, status
from sqlalchemy import select

from app.dependencies import CurrentUser, DbSession
from app.models import Business, UserRole
from app.schemas.business import BusinessCreate, BusinessRead, BusinessUpdate
from app.utils.exceptions import forbidden
from app.utils.permissions import ensure_owner_or_admin, ensure_owner_role

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.post("", response_model=BusinessRead, status_code=status.HTTP_201_CREATED)
async def create_business(payload: BusinessCreate, db: DbSession, current_user: CurrentUser) -> Business:
    ensure_owner_role(current_user)
    business = Business(owner_id=current_user.id, **payload.model_dump())
    db.add(business)
    await db.commit()
    await db.refresh(business)
    return business


@router.get("", response_model=list[BusinessRead])
async def list_businesses(db: DbSession, current_user: CurrentUser) -> list[Business]:
    if current_user.role == UserRole.PLATFORM_ADMIN:
        result = await db.execute(select(Business).order_by(Business.id))
    else:
        result = await db.execute(
            select(Business)
            .where(Business.owner_id == current_user.id, Business.is_active.is_(True))
            .order_by(Business.id)
        )
    return list(result.scalars().all())


@router.get("/{business_id}", response_model=BusinessRead)
async def get_business(business_id: int, db: DbSession, current_user: CurrentUser) -> Business:
    return await ensure_owner_or_admin(db, business_id, current_user)


@router.put("/{business_id}", response_model=BusinessRead)
async def update_business(
    business_id: int,
    payload: BusinessUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> Business:
    business = await ensure_owner_or_admin(db, business_id, current_user)
    if current_user.role != UserRole.PLATFORM_ADMIN and business.owner_id != current_user.id:
        raise forbidden("You do not have permission for this business")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(business, field, value)
    await db.commit()
    await db.refresh(business)
    return business


@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(business_id: int, db: DbSession, current_user: CurrentUser) -> None:
    business = await ensure_owner_or_admin(db, business_id, current_user)
    business.is_active = False
    await db.commit()
