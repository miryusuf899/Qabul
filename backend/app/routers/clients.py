from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from app.dependencies import CurrentUser, DbSession
from app.models import Client
from app.schemas.client import ClientRead, ClientUpdate
from app.utils.exceptions import not_found
from app.utils.permissions import ensure_owner_or_admin

router = APIRouter(tags=["clients"])


async def get_client_for_user(db: DbSession, client_id: int, current_user: CurrentUser) -> Client:
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if client is None:
        raise not_found("Client not found")
    await ensure_owner_or_admin(db, client.business_id, current_user)
    return client


@router.get("/businesses/{business_id}/clients", response_model=list[ClientRead])
async def list_clients(business_id: int, db: DbSession, current_user: CurrentUser) -> list[Client]:
    await ensure_owner_or_admin(db, business_id, current_user)
    result = await db.execute(
        select(Client).where(Client.business_id == business_id).order_by(Client.id)
    )
    return list(result.scalars().all())


@router.get("/clients/{client_id}", response_model=ClientRead)
async def get_client(client_id: int, db: DbSession, current_user: CurrentUser) -> Client:
    return await get_client_for_user(db, client_id, current_user)


@router.put("/clients/{client_id}", response_model=ClientRead)
async def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> Client:
    client = await get_client_for_user(db, client_id, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    await db.commit()
    await db.refresh(client)
    return client
