from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message

import storage
from filters import IsAllowedUser
from keyboards import channels_pagination_kb
from services.telethon_client import add_tracked_channel, remove_tracked_channel

router = Router()
router.message.filter(IsAllowedUser())
router.callback_query.filter(IsAllowedUser())


async def _delete_previous(chat_id: int, bot) -> None:
    last_id = storage.get_last_message(chat_id)
    if last_id:
        try:
            await bot.delete_message(chat_id, last_id)
        except Exception:
            pass
        storage.clear_last_message(chat_id)


def _format_channel(info: dict) -> str:
    return (
        f"<b>{info.get('title', 'Без названия')}</b>\n"
        f"Ссылка: {info.get('link') or '—'}\n"
        f"Подписчиков: {info.get('subscribers', 0)}\n"
        f"Просмотров на последнем посте: {info.get('last_post_views', 0)}\n"
        f"Обновлено: {info.get('updated_at', '—')}"
    )


@router.message(F.text == "Каналы")
async def on_channels_button(message: Message) -> None:
    await _delete_previous(message.chat.id, message.bot)

    data = storage.load_channels_data()
    if not data:
        sent = await message.answer(
            "Актуальные каналы\n\nПока нет отслеживаемых каналов. "
            "Добавьте канал командой /addchannel @username "
            "(аккаунт-администратор должен быть добавлен в канал заранее)."
        )
        storage.set_last_message(message.chat.id, sent.message_id)
        return

    info = data[0]
    kb = channels_pagination_kb(0, len(data))
    caption = "Актуальные каналы\n\n" + _format_channel(info)

    if info.get("avatar_path"):
        try:
            sent = await message.answer_photo(FSInputFile(info["avatar_path"]), caption=caption, reply_markup=kb)
        except Exception:
            sent = await message.answer(caption, reply_markup=kb)
    else:
        sent = await message.answer(caption, reply_markup=kb)

    storage.set_last_message(message.chat.id, sent.message_id)


@router.callback_query(F.data.startswith("chan_"))
async def on_channels_pagination(callback: CallbackQuery) -> None:
    if callback.data == "chan_noop":
        await callback.answer()
        return

    action, index_str = callback.data.rsplit("_", 1)
    index = int(index_str)

    data = storage.load_channels_data()
    if not data:
        await callback.answer("Нет данных")
        return

    total = len(data)
    if action == "chan_next":
        index = (index + 1) % total
    elif action == "chan_prev":
        index = (index - 1) % total

    info = data[index]
    kb = channels_pagination_kb(index, total)
    caption = "Актуальные каналы\n\n" + _format_channel(info)

    try:
        if info.get("avatar_path"):
            media = InputMediaPhoto(media=FSInputFile(info["avatar_path"]), caption=caption)
            await callback.message.edit_media(media, reply_markup=kb)
        else:
            await callback.message.edit_text(caption, reply_markup=kb)
    except Exception:
        pass

    await callback.answer()


@router.message(Command("addchannel"))
async def on_add_channel(message: Message) -> None:
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Использование: /addchannel @username")
        return

    username = args[1].strip()
    try:
        await add_tracked_channel(username)
        await message.answer(f"Канал {username} добавлен и обновлён.")
    except Exception as e:
        await message.answer(f"Ошибка при добавлении канала: {e}")


@router.message(Command("removechannel"))
async def on_remove_channel(message: Message) -> None:
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Использование: /removechannel @username")
        return

    username = args[1].strip()
    await remove_tracked_channel(username)
    await message.answer(f"Канал {username} убран из отслеживания.")
