from __future__ import annotations

import asyncio
from datetime import timedelta, time
from decimal import Decimal

from sqlalchemy import delete, select

from app.db import AsyncSessionLocal
from app.models import (
    AIMessage,
    Booking,
    BookingSource,
    BookingStatus,
    Business,
    Client,
    Notification,
    NotificationStatus,
    Service,
    Staff,
    StaffService,
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
    User,
    UserRole,
    WorkingHour,
)
from app.services.password_service import hash_password
from app.utils.datetime_utils import combine_local, now_in_timezone

OWNER_EMAIL = "owner@example.com"
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
                description="Premium barbershop and grooming studio in Dushanbe",
                business_type="barbershop",
                phone="+992900112233",
                address="Dushanbe, Rudaki Avenue 45",
                timezone="Asia/Dushanbe",
                is_active=True,
                ai_enabled=True,
            )
            db.add(business)
            await db.flush()
        else:
            business.description = "Premium barbershop and grooming studio in Dushanbe"
            business.phone = "+992900112233"
            business.address = "Dushanbe, Rudaki Avenue 45"
            business.ai_enabled = True

        service_specs = [
            ("Мужская стрижка", "Классическая или fade-стрижка с консультацией мастера", Decimal("70.00"), 40),
            ("Борода и контур", "Коррекция бороды, горячее полотенце и финальный уход", Decimal("45.00"), 30),
            ("Стрижка + борода", "Полный grooming-комплекс для постоянных клиентов", Decimal("105.00"), 70),
            ("Детская стрижка", "Быстрая аккуратная стрижка для детей до 12 лет", Decimal("45.00"), 30),
            ("Укладка", "Финишная укладка перед встречей или мероприятием", Decimal("35.00"), 25),
            ("Окрашивание камуфляж", "Мягкое тонирование седины с естественным результатом", Decimal("130.00"), 75),
        ]
        services_by_name: dict[str, Service] = {}
        for name, description, price, duration in service_specs:
            result = await db.execute(
                select(Service).where(Service.business_id == business.id, Service.name == name)
            )
            service = result.scalar_one_or_none()
            if service is None:
                service = Service(
                    business_id=business.id,
                    name=name,
                    description=description,
                    price=price,
                    duration_minutes=duration,
                    is_active=True,
                )
                db.add(service)
                await db.flush()
            else:
                service.description = description
                service.price = price
                service.duration_minutes = duration
                service.is_active = True
            services_by_name[name] = service

        staff_by_name: dict[str, Staff] = {}
        staff_specs = [
            ("Али Назаров", "+992901010101", "Fade, классика, борода"),
            ("Саид Каримов", "+992902020202", "Борода, уход, камуфляж"),
            ("Мадина Юсупова", "+992903030303", "Укладки, детские стрижки"),
            ("Рустам Мирзоев", "+992904040404", "Премиум grooming"),
        ]
        for name, phone, specialization in staff_specs:
            result = await db.execute(
                select(Staff).where(Staff.business_id == business.id, Staff.full_name == name)
            )
            staff = result.scalar_one_or_none()
            if staff is None:
                staff = Staff(
                    business_id=business.id,
                    full_name=name,
                    phone=phone,
                    specialization=specialization,
                    is_active=True,
                )
                db.add(staff)
                await db.flush()
            else:
                staff.phone = phone
                staff.specialization = specialization
                staff.is_active = True
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

        await db.execute(delete(Notification).where(Notification.business_id == business.id))
        await db.execute(delete(AIMessage).where(AIMessage.business_id == business.id))
        await db.execute(delete(Booking).where(Booking.business_id == business.id))
        await db.execute(delete(Client).where(Client.business_id == business.id))
        await db.execute(delete(Subscription).where(Subscription.business_id == business.id))
        await db.flush()

        db.add(
            Subscription(
                business_id=business.id,
                plan=SubscriptionPlan.PRO,
                status=SubscriptionStatus.ACTIVE,
                bookings_limit=2500,
                ai_messages_limit=10000,
                starts_at=now_in_timezone(business.timezone) - timedelta(days=14),
                ends_at=now_in_timezone(business.timezone) + timedelta(days=350),
            )
        )

        client_specs = [
            ("Фаррух Сафаров", "+992917100001", 710000001, "farrukh_safar"),
            ("Мунира Абдуллоева", "+992917100002", 710000002, "munira_a"),
            ("Далер Рахимов", "+992917100003", 710000003, "daler_r"),
            ("Азиза Каримова", "+992917100004", 710000004, "aziza_k"),
            ("Сомон Саидов", "+992917100005", 710000005, "somon_s"),
            ("Шахром Исмоилов", "+992917100006", 710000006, "shahrom_i"),
            ("Нилуфар Юлдошева", "+992917100007", 710000007, "nilufar_y"),
            ("Темур Холматов", "+992917100008", 710000008, "temur_h"),
            ("Зарина Мирзоева", "+992917100009", 710000009, "zarina_m"),
            ("Комрон Давлатов", "+992917100010", 710000010, "komron_d"),
            ("Сабина Одинаева", "+992917100011", 710000011, "sabina_o"),
            ("Умед Хайдаров", "+992917100012", 710000012, "umed_h"),
        ]
        clients: list[Client] = []
        for full_name, phone, telegram_id, username in client_specs:
            client = Client(
                business_id=business.id,
                full_name=full_name,
                phone=phone,
                telegram_id=telegram_id,
                telegram_username=username,
                total_visits=0,
            )
            db.add(client)
            clients.append(client)
        await db.flush()

        today = now_in_timezone(business.timezone).date()
        booking_specs = [
            (-13, time(10, 0), "Фаррух Сафаров", "Али Назаров", "Мужская стрижка", "completed", "telegram_ai"),
            (-12, time(12, 0), "Мунира Абдуллоева", "Мадина Юсупова", "Укладка", "completed", "dashboard"),
            (-11, time(15, 0), "Далер Рахимов", "Саид Каримов", "Борода и контур", "completed", "telegram_manual"),
            (-10, time(11, 0), "Азиза Каримова", "Мадина Юсупова", "Детская стрижка", "completed", "dashboard"),
            (-9, time(18, 0), "Сомон Саидов", "Рустам Мирзоев", "Стрижка + борода", "completed", "telegram_ai"),
            (-8, time(16, 30), "Шахром Исмоилов", "Саид Каримов", "Окрашивание камуфляж", "completed", "dashboard"),
            (-7, time(13, 0), "Нилуфар Юлдошева", "Мадина Юсупова", "Укладка", "completed", "telegram_ai"),
            (-6, time(10, 30), "Темур Холматов", "Али Назаров", "Мужская стрижка", "completed", "dashboard"),
            (-5, time(14, 0), "Зарина Мирзоева", "Мадина Юсупова", "Детская стрижка", "cancelled", "telegram_ai"),
            (-4, time(17, 0), "Комрон Давлатов", "Рустам Мирзоев", "Стрижка + борода", "completed", "telegram_manual"),
            (-3, time(12, 30), "Сабина Одинаева", "Мадина Юсупова", "Укладка", "completed", "dashboard"),
            (-2, time(19, 0), "Умед Хайдаров", "Саид Каримов", "Борода и контур", "no_show", "telegram_ai"),
            (-1, time(11, 30), "Фаррух Сафаров", "Али Назаров", "Мужская стрижка", "completed", "dashboard"),
            (-1, time(16, 0), "Далер Рахимов", "Рустам Мирзоев", "Стрижка + борода", "completed", "telegram_ai"),
            (0, time(9, 30), "Мунира Абдуллоева", "Мадина Юсупова", "Укладка", "confirmed", "dashboard"),
            (0, time(11, 0), "Сомон Саидов", "Али Назаров", "Мужская стрижка", "confirmed", "telegram_ai"),
            (0, time(13, 30), "Шахром Исмоилов", "Саид Каримов", "Борода и контур", "pending", "telegram_ai"),
            (0, time(16, 30), "Зарина Мирзоева", "Рустам Мирзоев", "Окрашивание камуфляж", "confirmed", "telegram_manual"),
            (1, time(10, 0), "Темур Холматов", "Али Назаров", "Мужская стрижка", "confirmed", "dashboard"),
            (1, time(12, 0), "Нилуфар Юлдошева", "Мадина Юсупова", "Детская стрижка", "confirmed", "telegram_ai"),
            (2, time(15, 0), "Комрон Давлатов", "Рустам Мирзоев", "Стрижка + борода", "confirmed", "telegram_ai"),
            (3, time(18, 30), "Сабина Одинаева", "Мадина Юсупова", "Укладка", "pending", "telegram_ai"),
        ]

        clients_by_name = {client.full_name: client for client in clients}
        services_by_id = {service.id: service for service in services_by_name.values()}
        bookings: list[Booking] = []
        for day_offset, start_at, client_name, staff_name, service_name, status_name, source_name in booking_specs:
            service = services_by_name[service_name]
            start_time = combine_local(today + timedelta(days=day_offset), start_at, business.timezone)
            status_value = BookingStatus(status_name)
            booking = Booking(
                business_id=business.id,
                client_id=clients_by_name[client_name].id,
                staff_id=staff_by_name[staff_name].id,
                service_id=service.id,
                start_time=start_time,
                end_time=start_time + timedelta(minutes=service.duration_minutes),
                status=status_value,
                source=BookingSource(source_name),
                note="Демо-запись для проверки dashboard" if day_offset <= 0 else "Будущая запись клиента",
                cancel_reason="Клиент перенёс визит" if status_value == BookingStatus.CANCELLED else None,
            )
            db.add(booking)
            bookings.append(booking)
        await db.flush()

        visits_by_client: dict[int, int] = {}
        last_visit_by_client = {}
        for booking in bookings:
            if booking.status in {BookingStatus.COMPLETED, BookingStatus.NO_SHOW}:
                visits_by_client[booking.client_id] = visits_by_client.get(booking.client_id, 0) + 1
                last_visit_by_client[booking.client_id] = max(
                    last_visit_by_client.get(booking.client_id, booking.start_time),
                    booking.start_time,
                )
        for client in clients:
            client.total_visits = visits_by_client.get(client.id, 0)
            client.last_visit_at = last_visit_by_client.get(client.id)

        for booking in bookings[-8:]:
            client = next(client for client in clients if client.id == booking.client_id)
            db.add(
                Notification(
                    business_id=business.id,
                    client_id=client.id,
                    booking_id=booking.id,
                    type="booking_reminder",
                    message=f"Напоминание: {booking.start_time:%d.%m %H:%M}, {services_by_id[booking.service_id].name}",
                    status=NotificationStatus.SENT if booking.start_time.date() <= today else NotificationStatus.PENDING,
                    scheduled_at=booking.start_time - timedelta(hours=2),
                    sent_at=booking.start_time - timedelta(hours=2) if booking.start_time.date() <= today else None,
                )
            )

        ai_examples = [
            (
                clients_by_name["Сомон Саидов"],
                "Можно сегодня на стрижку после 11?",
                "Да, свободно 11:00 у Али Назарова. Записать вас?",
                "booking_request",
                "suggested_slot",
            ),
            (
                clients_by_name["Шахром Исмоилов"],
                "Сколько стоит борода?",
                "Борода и контур стоит 45 TJS, длительность 30 минут.",
                "price_question",
                "answered",
            ),
            (
                clients_by_name["Нилуфар Юлдошева"],
                "Запишите ребёнка завтра днём",
                "Есть окно завтра в 12:00 у Мадины. Я поставил предварительную запись.",
                "booking_request",
                "created_pending_booking",
            ),
        ]
        for client, user_message, ai_response, intent, action_taken in ai_examples:
            db.add(
                AIMessage(
                    business_id=business.id,
                    client_id=client.id,
                    telegram_id=client.telegram_id,
                    user_message=user_message,
                    ai_response=ai_response,
                    intent=intent,
                    action_taken=action_taken,
                )
            )

        await db.commit()
        print("Demo data is ready")
        print(f"Owner: {OWNER_EMAIL} / {OWNER_PASSWORD}")
        print(f"Business ID: {business.id}")
        print(f"Services: {len(services_by_name)}")
        print(f"Staff: {len(staff_by_name)}")
        print(f"Clients: {len(clients)}")
        print(f"Bookings: {len(bookings)}")


if __name__ == "__main__":
    asyncio.run(seed())
