from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import AIMessage, Booking, BookingSource, BookingStatus, Business, Client, Service, Staff, StaffService, WorkingHour
from app.schemas.ai import AIChatRequest, AIChatResponse
from app.schemas.booking import BookingCreate
from app.services.booking_service import cancel_booking, create_booking, find_or_create_client, get_available_slots
from app.utils.datetime_utils import combine_local, now_in_timezone
from app.utils.exceptions import not_found

PENDING_PREFIX = "awaiting_confirmation:"
YES_WORDS = {"да", "ага", "подтверждаю", "подтвердить", "ок", "okay", "yes", "конечно"}


@dataclass
class ParsedBookingIntent:
    service: Service | None
    staff: Staff | None
    slot_date: date | None
    slot_time: time | None
    after_noon: bool = False


def _norm(value: str) -> str:
    value = value.lower().replace("ё", "е")
    value = re.sub(r"[^a-zа-я0-9:+ ]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _stem(word: str) -> str:
    word = _norm(word)
    return word[: max(4, min(len(word), 6))]


def _money(value: Decimal) -> str:
    if value == value.to_integral_value():
        return str(int(value))
    return str(value)


async def _get_business(db: AsyncSession, business_id: int) -> Business:
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    if business is None or not business.is_active:
        raise not_found("Business not found")
    return business


async def _active_services(db: AsyncSession, business_id: int) -> list[Service]:
    result = await db.execute(
        select(Service)
        .where(Service.business_id == business_id, Service.is_active.is_(True))
        .order_by(Service.id)
    )
    return list(result.scalars().all())


async def _active_staff(db: AsyncSession, business_id: int) -> list[Staff]:
    result = await db.execute(
        select(Staff)
        .where(Staff.business_id == business_id, Staff.is_active.is_(True))
        .order_by(Staff.id)
    )
    return list(result.scalars().all())


def _match_service(message: str, services: list[Service]) -> Service | None:
    normalized_message = _norm(message)
    for service in services:
        service_name = _norm(service.name)
        if service_name in normalized_message:
            return service
        service_words = [word for word in service_name.split() if len(word) > 3]
        if any(_stem(word) in normalized_message for word in service_words):
            return service
    return None


def _match_staff(message: str, staff_members: list[Staff]) -> Staff | None:
    normalized_message = _norm(message)
    for staff in staff_members:
        if _norm(staff.full_name) in normalized_message:
            return staff
    return None


def _parse_date(message: str, business: Business) -> date | None:
    normalized = _norm(message)
    today = now_in_timezone(business.timezone).date()
    if "послезавтра" in normalized:
        return today + timedelta(days=2)
    if "завтра" in normalized:
        return today + timedelta(days=1)
    if "сегодня" in normalized:
        return today
    iso_match = re.search(r"\b(20\d{2})-(\d{2})-(\d{2})\b", normalized)
    if iso_match:
        return date(int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3)))
    dotted_match = re.search(r"\b(\d{1,2})[./-](\d{1,2})(?:[./-](20\d{2}))?\b", normalized)
    if dotted_match:
        day = int(dotted_match.group(1))
        month = int(dotted_match.group(2))
        year = int(dotted_match.group(3) or today.year)
        return date(year, month, day)
    return None


def _parse_time(message: str) -> time | None:
    normalized = _norm(message)
    match = re.search(r"(?:в|на|к|^)\s*(\d{1,2})(?::(\d{2}))?\b", normalized)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    if 0 <= hour <= 23 and 0 <= minute <= 59:
        return time(hour, minute)
    return None


def _parse_booking_intent(
    message: str,
    business: Business,
    services: list[Service],
    staff_members: list[Staff],
) -> ParsedBookingIntent:
    normalized = _norm(message)
    return ParsedBookingIntent(
        service=_match_service(normalized, services),
        staff=_match_staff(normalized, staff_members),
        slot_date=_parse_date(normalized, business),
        slot_time=_parse_time(normalized),
        after_noon="после обеда" in normalized or "послеобед" in normalized,
    )


def _detect_intent(message: str) -> str:
    normalized = _norm(message)
    if normalized in YES_WORDS or any(word == normalized for word in YES_WORDS):
        return "confirm_booking"
    if any(word in normalized for word in ["отмен", "cancel"]):
        return "cancel_booking"
    if any(word in normalized for word in ["мои записи", "записи", "бронь", "booking"]):
        return "ask_bookings"
    if any(word in normalized for word in ["цена", "цены", "прайс", "стоим"]):
        return "ask_prices"
    if any(word in normalized for word in ["услуг", "сервис"]):
        return "ask_services"
    if any(word in normalized for word in ["адрес", "где вы", "локац"]):
        return "ask_address"
    if any(word in normalized for word in ["телефон", "номер", "позвон"]):
        return "ask_phone"
    if any(word in normalized for word in ["время", "график", "работаете", "открыт"]):
        return "ask_working_hours"
    if any(word in normalized for word in ["запиши", "запис", "хочу", "бронь", "стриж", "бород"]):
        return "book_appointment"
    if any(word in normalized for word in ["администратор", "человек", "оператор"]):
        return "human_help"
    return "unknown"


def _services_reply(services: list[Service], include_prices: bool = False) -> str:
    if not services:
        return "Пока нет доступных услуг."
    parts = []
    for service in services:
        if include_prices:
            parts.append(f"{service.name} — {_money(service.price)} сомони, {service.duration_minutes} мин.")
        else:
            parts.append(f"{service.name} ({service.duration_minutes} мин.)")
    return "Доступные услуги: " + "; ".join(parts)


async def _working_hours_reply(db: AsyncSession, business_id: int) -> str:
    result = await db.execute(
        select(WorkingHour)
        .where(WorkingHour.business_id == business_id)
        .order_by(WorkingHour.day_of_week)
    )
    rows = list(result.scalars().all())
    if not rows:
        return "Рабочие часы пока не настроены."
    names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    chunks = []
    for row in rows:
        if row.is_closed:
            chunks.append(f"{names[row.day_of_week]}: закрыто")
        else:
            chunks.append(f"{names[row.day_of_week]}: {row.open_time:%H:%M}-{row.close_time:%H:%M}")
    return "График работы: " + "; ".join(chunks)


async def _record_message(
    db: AsyncSession,
    business_id: int,
    client_id: int | None,
    telegram_id: int | None,
    user_message: str,
    response: AIChatResponse,
) -> None:
    db.add(
        AIMessage(
            business_id=business_id,
            client_id=client_id,
            telegram_id=telegram_id,
            user_message=user_message,
            ai_response=response.reply,
            intent=response.intent,
            action_taken=response.action_taken,
        )
    )
    await db.commit()


async def _get_client(db: AsyncSession, business_id: int, payload: AIChatRequest) -> Client | None:
    if payload.telegram_id is None and payload.phone is None and payload.client_name is None:
        return None
    return await find_or_create_client(
        db,
        business_id,
        phone=payload.phone,
        telegram_id=payload.telegram_id,
        full_name=payload.client_name or payload.telegram_username,
        telegram_username=payload.telegram_username,
    )


async def _recent_pending(db: AsyncSession, business_id: int, client: Client | None, telegram_id: int | None) -> AIMessage | None:
    conditions = [AIMessage.business_id == business_id, AIMessage.action_taken.like(f"{PENDING_PREFIX}%")]
    if client is not None:
        conditions.append(AIMessage.client_id == client.id)
    elif telegram_id is not None:
        conditions.append(AIMessage.telegram_id == telegram_id)
    else:
        return None
    result = await db.execute(
        select(AIMessage)
        .where(*conditions)
        .order_by(AIMessage.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


def _pending_payload(message: AIMessage) -> dict:
    if not message.action_taken or not message.action_taken.startswith(PENDING_PREFIX):
        return {}
    try:
        return json.loads(message.action_taken.removeprefix(PENDING_PREFIX))
    except json.JSONDecodeError:
        return {}


async def _choose_staff_for_slot(
    db: AsyncSession,
    business_id: int,
    service_id: int,
    slot_date: date,
    slot_time: time,
    requested_staff_id: int | None,
) -> int | None:
    if requested_staff_id is not None:
        slots = await get_available_slots(db, business_id, service_id, slot_date, staff_id=requested_staff_id)
        return requested_staff_id if slot_time.strftime("%H:%M") in slots else None

    result = await db.execute(
        select(Staff.id)
        .join(StaffService, StaffService.staff_id == Staff.id)
        .where(
            Staff.business_id == business_id,
            Staff.is_active.is_(True),
            StaffService.service_id == service_id,
        )
        .order_by(Staff.id)
    )
    for staff_id in result.scalars().all():
        slots = await get_available_slots(db, business_id, service_id, slot_date, staff_id=staff_id)
        if slot_time.strftime("%H:%M") in slots:
            return staff_id
    return None


async def _confirm_pending_booking(
    db: AsyncSession,
    business: Business,
    client: Client | None,
    pending_message: AIMessage,
) -> AIChatResponse:
    data = _pending_payload(pending_message)
    if not data:
        return AIChatResponse(
            reply="Не нашёл запись для подтверждения. Напишите, пожалуйста, услугу, дату и время.",
            intent="confirm_booking",
            action_taken="missing_pending_booking",
        )
    try:
        payload = BookingCreate(
            client_name=data.get("client_name") or (client.full_name if client else None),
            client_phone=data.get("client_phone") or (client.phone if client else None),
            telegram_id=data.get("telegram_id"),
            telegram_username=data.get("telegram_username"),
            staff_id=int(data["staff_id"]),
            service_id=int(data["service_id"]),
            start_time=datetime.fromisoformat(data["start_time"]),
            note="Created by AI administrator",
        )
        booking = await create_booking(db, business.id, payload, source=BookingSource.TELEGRAM_AI)
    except HTTPException as exc:
        return AIChatResponse(
            reply=f"Не получилось создать запись: {exc.detail}. Попробуем другое время?",
            intent="confirm_booking",
            action_taken="booking_failed",
        )

    pending_message.action_taken = f"confirmed_booking:{booking.id}"
    await db.flush()
    return AIChatResponse(
        reply=(
            f"Готово! Запись подтверждена на {booking.start_time:%d.%m.%Y %H:%M}: "
            f"{booking.service.name}, мастер {booking.staff.full_name}."
        ),
        intent="confirm_booking",
        action_taken=f"booking_created:{booking.id}",
    )


async def _list_client_bookings(db: AsyncSession, business: Business, client: Client | None) -> AIChatResponse:
    if client is None:
        return AIChatResponse(
            reply="Я могу показать записи, если вы пишете из Telegram или указали телефон.",
            intent="ask_bookings",
            action_taken="client_not_identified",
        )
    now = now_in_timezone(business.timezone)
    result = await db.execute(
        select(Booking)
        .where(
            Booking.business_id == business.id,
            Booking.client_id == client.id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            Booking.start_time >= now,
        )
        .order_by(Booking.start_time)
        .limit(5)
    )
    bookings = list(result.scalars().all())
    if not bookings:
        return AIChatResponse(reply="У вас пока нет ближайших записей.", intent="ask_bookings", action_taken="listed_bookings")
    lines = [f"{booking.start_time:%d.%m %H:%M}" for booking in bookings]
    return AIChatResponse(
        reply="Ваши ближайшие записи: " + "; ".join(lines),
        intent="ask_bookings",
        action_taken="listed_bookings",
    )


async def _cancel_nearest_booking(db: AsyncSession, business: Business, client: Client | None) -> AIChatResponse:
    if client is None:
        return AIChatResponse(
            reply="Чтобы отменить запись, мне нужно узнать вас по Telegram или телефону.",
            intent="cancel_booking",
            action_taken="client_not_identified",
        )
    now = now_in_timezone(business.timezone)
    result = await db.execute(
        select(Booking)
        .where(
            Booking.business_id == business.id,
            Booking.client_id == client.id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            Booking.start_time >= now,
        )
        .order_by(Booking.start_time)
        .limit(1)
    )
    booking = result.scalar_one_or_none()
    if booking is None:
        return AIChatResponse(reply="Не нашёл активную запись для отмены.", intent="cancel_booking", action_taken="nothing_to_cancel")
    await cancel_booking(db, booking.id, "Cancelled via AI chat")
    return AIChatResponse(reply="Запись отменена.", intent="cancel_booking", action_taken=f"booking_cancelled:{booking.id}")


def _date_label(slot_date: date, business: Business) -> str:
    today = now_in_timezone(business.timezone).date()
    if slot_date == today:
        return "Сегодня"
    if slot_date == today + timedelta(days=1):
        return "Завтра"
    return slot_date.strftime("%d.%m.%Y")


async def _handle_booking_intent(
    db: AsyncSession,
    business: Business,
    payload: AIChatRequest,
    client: Client | None,
    services: list[Service],
) -> AIChatResponse:
    staff_members = await _active_staff(db, business.id)
    parsed = _parse_booking_intent(payload.message, business, services, staff_members)
    if parsed.service is None:
        return AIChatResponse(
            reply="Какую услугу хотите? " + _services_reply(services, include_prices=True),
            intent="book_appointment",
            action_taken="asked_service",
        )
    if parsed.slot_date is None:
        return AIChatResponse(
            reply=f"На какой день записать на услугу «{parsed.service.name}»?",
            intent="book_appointment",
            action_taken="asked_date",
        )

    slots = await get_available_slots(
        db,
        business.id,
        parsed.service.id,
        parsed.slot_date,
        staff_id=parsed.staff.id if parsed.staff else None,
    )
    if parsed.after_noon:
        slots = [slot for slot in slots if slot >= "12:00"]
    if not slots:
        return AIChatResponse(
            reply="На это время свободных слотов нет. Напишите другой день или услугу.",
            intent="book_appointment",
            action_taken="no_slots",
        )

    if parsed.slot_time is None:
        return AIChatResponse(
            reply=f"{_date_label(parsed.slot_date, business)} свободно: {', '.join(slots[:6])}. Какое время удобно?",
            intent="book_appointment",
            action_taken="suggested_slots",
        )

    requested_slot = parsed.slot_time.strftime("%H:%M")
    staff_id = await _choose_staff_for_slot(
        db,
        business.id,
        parsed.service.id,
        parsed.slot_date,
        parsed.slot_time,
        parsed.staff.id if parsed.staff else None,
    )
    if requested_slot not in slots or staff_id is None:
        return AIChatResponse(
            reply=f"{requested_slot} занято. Есть свободно: {', '.join(slots[:6])}.",
            intent="book_appointment",
            action_taken="suggested_slots",
        )

    start_time = combine_local(parsed.slot_date, parsed.slot_time, business.timezone)
    pending = {
        "business_id": business.id,
        "client_name": payload.client_name or payload.telegram_username or (client.full_name if client else None),
        "client_phone": payload.phone or (client.phone if client else None),
        "telegram_id": payload.telegram_id,
        "telegram_username": payload.telegram_username,
        "staff_id": staff_id,
        "service_id": parsed.service.id,
        "start_time": start_time.isoformat(),
    }
    return AIChatResponse(
        reply=f"{_date_label(parsed.slot_date, business)} в {requested_slot} свободно. Подтвердить запись?",
        intent="book_appointment",
        action_taken=PENDING_PREFIX + json.dumps(pending, ensure_ascii=False),
    )


async def handle_ai_chat(db: AsyncSession, payload: AIChatRequest) -> AIChatResponse:
    business = await _get_business(db, payload.business_id)
    client = await _get_client(db, business.id, payload)
    intent = _detect_intent(payload.message)
    services = await _active_services(db, business.id)
    pending = await _recent_pending(db, business.id, client, payload.telegram_id)

    if intent == "confirm_booking" and pending is not None:
        response = await _confirm_pending_booking(db, business, client, pending)
    elif intent == "ask_services":
        response = AIChatResponse(reply=_services_reply(services), intent=intent, action_taken="listed_services")
    elif intent == "ask_prices":
        response = AIChatResponse(reply=_services_reply(services, include_prices=True), intent=intent, action_taken="listed_prices")
    elif intent == "ask_working_hours":
        response = AIChatResponse(
            reply=await _working_hours_reply(db, business.id),
            intent=intent,
            action_taken="listed_working_hours",
        )
    elif intent == "ask_address":
        response = AIChatResponse(
            reply=business.address or "Адрес пока не указан.",
            intent=intent,
            action_taken="shared_address",
        )
    elif intent == "ask_phone":
        response = AIChatResponse(
            reply=business.phone or "Телефон пока не указан.",
            intent=intent,
            action_taken="shared_phone",
        )
    elif intent == "ask_bookings":
        response = await _list_client_bookings(db, business, client)
    elif intent == "cancel_booking":
        response = await _cancel_nearest_booking(db, business, client)
    elif intent == "book_appointment":
        response = await _handle_booking_intent(db, business, payload, client, services)
    elif intent == "human_help":
        response = AIChatResponse(
            reply="Я передам ваш вопрос администратору.",
            intent=intent,
            action_taken="human_help_requested",
        )
    else:
        response = AIChatResponse(
            reply="Я уточню у администратора. Могу рассказать об услугах, ценах или записать вас на удобное время.",
            intent="unknown",
            action_taken="fallback",
        )

    provider_ready = settings.ai_provider == "mock" or not any(
        [settings.gemini_api_key, settings.groq_api_key, settings.openai_api_key]
    )
    if provider_ready and response.action_taken is None:
        response.action_taken = "mock_mode"

    await _record_message(db, business.id, client.id if client else None, payload.telegram_id, payload.message, response)
    return response
