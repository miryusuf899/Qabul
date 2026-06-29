from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from app.bot.handlers import router
from app.config import settings


async def main() -> None:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")

    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Начать"),
            BotCommand(command="services", description="Услуги и цены"),
            BotCommand(command="bookings", description="Мои записи"),
            BotCommand(command="cancel", description="Отменить запись"),
            BotCommand(command="help", description="Помощь"),
        ]
    )
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
