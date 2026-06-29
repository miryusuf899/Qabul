from __future__ import annotations

import httpx
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards import main_keyboard
from app.config import settings

router = Router()


async def _send_to_ai(message: Message, text: str) -> str:
    user = message.from_user
    payload = {
        "business_id": settings.default_business_id,
        "telegram_id": user.id if user else None,
        "telegram_username": user.username if user else None,
        "client_name": user.full_name if user else None,
        "message": text,
    }
    url = f"{settings.backend_api_url.rstrip('/')}/ai/chat"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
    except httpx.HTTPError:
        return "Сервис временно недоступен. Попробуйте чуть позже."
    data = response.json()
    return data.get("reply") or "Я уточню у администратора."


@router.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer(
        "Здравствуйте! Я цифровой администратор Qabul.\n"
        "Я могу рассказать об услугах, ценах и записать вас на удобное время.\n"
        "Напишите, например: “Хочу завтра на стрижку в 15:00”.",
        reply_markup=main_keyboard(),
    )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(
        "Я могу показать услуги, цены, ваши записи и помочь записаться. "
        "Просто напишите обычным сообщением, что вам нужно.",
        reply_markup=main_keyboard(),
    )


@router.message(Command("services"))
async def services(message: Message) -> None:
    await message.answer(await _send_to_ai(message, "услуги и цены"), reply_markup=main_keyboard())


@router.message(Command("bookings"))
async def bookings(message: Message) -> None:
    await message.answer(await _send_to_ai(message, "мои записи"), reply_markup=main_keyboard())


@router.message(Command("cancel"))
async def cancel(message: Message) -> None:
    await message.answer(await _send_to_ai(message, "отменить запись"), reply_markup=main_keyboard())


@router.message(F.text)
async def plain_text(message: Message) -> None:
    await message.answer(await _send_to_ai(message, message.text or ""), reply_markup=main_keyboard())
