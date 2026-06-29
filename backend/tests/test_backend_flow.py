from __future__ import annotations

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db import Base, get_db
from app.main import create_app


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client

    await engine.dispose()


async def _auth_headers(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Miryusuf",
            "email": "owner@example.com",
            "phone": "+992900000000",
            "password": "123456",
        },
    )
    assert response.status_code == 201, response.text

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "123456"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _next_open_day() -> datetime:
    tz = ZoneInfo("Asia/Dushanbe")
    day = datetime.now(tz).date() + timedelta(days=1)
    while day.weekday() == 6:
        day += timedelta(days=1)
    return datetime.combine(day, time(15, 0), tzinfo=tz)


@pytest.mark.asyncio
async def test_backend_demo_flow(client: AsyncClient) -> None:
    headers = await _auth_headers(client)

    business_response = await client.post(
        "/api/v1/businesses",
        headers=headers,
        json={
            "name": "Barber Pro",
            "description": "Demo barbershop",
            "business_type": "barbershop",
            "phone": "+992900000000",
            "address": "Dushanbe, Rudaki",
            "timezone": "Asia/Dushanbe",
        },
    )
    assert business_response.status_code == 201, business_response.text
    business_id = business_response.json()["id"]

    service_response = await client.post(
        f"/api/v1/businesses/{business_id}/services",
        headers=headers,
        json={"name": "Стрижка", "price": "50.00", "duration_minutes": 30, "is_active": True},
    )
    assert service_response.status_code == 201, service_response.text
    service_id = service_response.json()["id"]

    staff_response = await client.post(
        f"/api/v1/businesses/{business_id}/staff",
        headers=headers,
        json={"full_name": "Али", "service_ids": [service_id]},
    )
    assert staff_response.status_code == 201, staff_response.text
    staff_id = staff_response.json()["id"]

    working_hours = [
        {
            "day_of_week": day,
            "open_time": None if day == 6 else "09:00",
            "close_time": None if day == 6 else "20:00",
            "is_closed": day == 6,
        }
        for day in range(7)
    ]
    response = await client.post(
        f"/api/v1/businesses/{business_id}/working-hours",
        headers=headers,
        json=working_hours,
    )
    assert response.status_code == 200, response.text

    start_time = _next_open_day()
    booking_payload = {
        "client_name": "Ali Client",
        "client_phone": "+992900000001",
        "staff_id": staff_id,
        "service_id": service_id,
        "start_time": start_time.isoformat(),
        "note": "Позвонить перед визитом",
    }
    response = await client.post(
        f"/api/v1/businesses/{business_id}/bookings",
        headers=headers,
        json=booking_payload,
    )
    assert response.status_code == 201, response.text
    booking_id = response.json()["id"]

    conflict_response = await client.post(
        f"/api/v1/businesses/{business_id}/bookings",
        headers=headers,
        json={**booking_payload, "client_phone": "+992900000002"},
    )
    assert conflict_response.status_code == 409, conflict_response.text

    outside_response = await client.post(
        f"/api/v1/businesses/{business_id}/bookings",
        headers=headers,
        json={**booking_payload, "start_time": start_time.replace(hour=21).isoformat()},
    )
    assert outside_response.status_code == 400, outside_response.text

    summary_response = await client.get(
        f"/api/v1/businesses/{business_id}/dashboard/summary",
        headers=headers,
    )
    assert summary_response.status_code == 200, summary_response.text
    assert summary_response.json()["month_bookings"] >= 1

    ai_start = start_time.replace(hour=16, minute=0)
    ai_response = await client.post(
        "/api/v1/ai/chat",
        json={
            "business_id": business_id,
            "telegram_id": 123456789,
            "telegram_username": "client_username",
            "message": f"Хочу {ai_start.date().isoformat()} на стрижку в 16:00",
        },
    )
    assert ai_response.status_code == 200, ai_response.text
    assert ai_response.json()["intent"] == "book_appointment"
    assert "Подтвердить" in ai_response.json()["reply"]

    confirm_response = await client.post(
        "/api/v1/ai/chat",
        json={
            "business_id": business_id,
            "telegram_id": 123456789,
            "telegram_username": "client_username",
            "message": "Да",
        },
    )
    assert confirm_response.status_code == 200, confirm_response.text
    assert confirm_response.json()["intent"] == "confirm_booking"
    assert "подтверждена" in confirm_response.json()["reply"].lower()

    cancel_response = await client.delete(f"/api/v1/bookings/{booking_id}", headers=headers)
    assert cancel_response.status_code == 200, cancel_response.text
    assert cancel_response.json()["status"] == "cancelled"
