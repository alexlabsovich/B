from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Content"), KeyboardButton(text="Каналы")]],
        resize_keyboard=True,
    )


def channels_pagination_kb(index: int, total: int) -> InlineKeyboardMarkup:
    row = []
    if total > 1:
        row = [
            InlineKeyboardButton(text="⬅️", callback_data=f"chan_prev_{index}"),
            InlineKeyboardButton(text=f"{index + 1}/{total}", callback_data="chan_noop"),
            InlineKeyboardButton(text="➡️", callback_data=f"chan_next_{index}"),
        ]
    return InlineKeyboardMarkup(inline_keyboard=[row] if row else [])
