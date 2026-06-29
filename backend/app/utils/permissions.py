from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Business, User, UserRole
from app.utils.exceptions import forbidden, not_found


async def ensure_owner_or_admin(db: AsyncSession, business_id: int, user: User) -> Business:
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    if not business or not business.is_active:
        raise not_found("Business not found")
    if user.role == UserRole.PLATFORM_ADMIN or business.owner_id == user.id:
        return business
    raise forbidden("You do not have permission for this business")


def ensure_owner_role(user: User) -> None:
    if user.role not in {UserRole.OWNER, UserRole.PLATFORM_ADMIN}:
        raise forbidden("Owner access required")
