from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/services"), KeyboardButton(text="/bookings")],
            [KeyboardButton(text="/cancel"), KeyboardButton(text="/help")],
        ],
        resize_keyboard=True,
    )
