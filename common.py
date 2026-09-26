from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

import storage
from filters import IsAllowedUser
from keyboards import main_menu_kb

router = Router()
router.message.filter(IsAllowedUser())


@router.message(CommandStart())
async def on_start(message: Message) -> None:
    last_id = storage.get_last_message(message.chat.id)
    if last_id:
        try:
            await message.bot.delete_message(message.chat.id, last_id)
        except Exception:
            pass
        storage.clear_last_message(message.chat.id)

    sent = await message.answer("DeadWeb активен, выберите задачу", reply_markup=main_menu_kb())
    storage.set_last_message(message.chat.id, sent.message_id)
