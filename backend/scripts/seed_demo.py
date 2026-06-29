from __future__ import annotations

import asyncio
from decimal import Decimal
from datetime import time

from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.models import Business, Service, Staff, StaffService, User, UserRole, WorkingHour
from app.services.password_service import hash_password

OWNER_EMAIL = "owner@qabul.test"
OWNER_PASSWORD = "password123"


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == OWNER_EMAIL))
        owner = result.scalar_one_or_none()
        if owner is None:
            owner = User(
                full_name="Demo Owner",
                email=OWNER_EMAIL,
                phone="+992900000000",
                password_hash=hash_password(OWNER_PASSWORD),
                role=UserRole.OWNER,
                is_active=True,
            )
            db.add(owner)
            await db.flush()

        result = await db.execute(
            select(Business).where(Business.owner_id == owner.id, Business.name == "Barber Pro")
        )
        business = result.scalar_one_or_none()
        if business is None:
            business = Business(
                owner_id=owner.id,
                name="Barber Pro",
                description="Demo barbershop for Qabul MVP",
                business_type="barbershop",
                phone="+992900000000",
                address="Dushanbe, Rudaki",
                timezone="Asia/Dushanbe",
                is_active=True,
                ai_enabled=True,
            )
            db.add(business)
            await db.flush()

        service_specs = [
            ("Стрижка", Decimal("50.00"), 30),
            ("Борода", Decimal("30.00"), 20),
            ("Стрижка + борода", Decimal("75.00"), 45),
            ("Укладка", Decimal("40.00"), 30),
        ]
        services_by_name: dict[str, Service] = {}
        for name, price, duration in service_specs:
            result = await db.execute(
                select(Service).where(Service.business_id == business.id, Service.name == name)
            )
            service = result.scalar_one_or_none()
            if service is None:
                service = Service(
                    business_id=business.id,
                    name=name,
                    price=price,
                    duration_minutes=duration,
                    is_active=True,
                )
                db.add(service)
                await db.flush()
            services_by_name[name] = service

        staff_by_name: dict[str, Staff] = {}
        for name in ["Али", "Саид"]:
            result = await db.execute(
                select(Staff).where(Staff.business_id == business.id, Staff.full_name == name)
            )
            staff = result.scalar_one_or_none()
            if staff is None:
                staff = Staff(business_id=business.id, full_name=name, is_active=True)
                db.add(staff)
                await db.flush()
            staff_by_name[name] = staff

        service_ids = [service.id for service in services_by_name.values()]
        for staff in staff_by_name.values():
            for service_id in service_ids:
                result = await db.execute(
                    select(StaffService).where(
                        StaffService.staff_id == staff.id,
                        StaffService.service_id == service_id,
                    )
                )
                if result.scalar_one_or_none() is None:
                    db.add(StaffService(staff_id=staff.id, service_id=service_id))

        for day in range(7):
            result = await db.execute(
                select(WorkingHour).where(
                    WorkingHour.business_id == business.id,
                    WorkingHour.day_of_week == day,
                )
            )
            row = result.scalar_one_or_none()
            values = {
                "is_closed": day == 6,
                "open_time": None if day == 6 else time(9, 0),
                "close_time": None if day == 6 else time(20, 0),
            }
            if row is None:
                db.add(WorkingHour(business_id=business.id, day_of_week=day, **values))
            else:
                for field, value in values.items():
                    setattr(row, field, value)

        await db.commit()
        print("Demo data is ready")
        print(f"Owner: {OWNER_EMAIL} / {OWNER_PASSWORD}")
        print(f"Business ID: {business.id}")


if __name__ == "__main__":
    asyncio.run(seed())
