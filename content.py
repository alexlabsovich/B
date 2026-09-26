import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import storage
from filters import IsAllowedUser
from keyboards import main_menu_kb
from services.openrouter_client import generate_post
from services.search import web_search

router = Router()
router.message.filter(IsAllowedUser())


class ContentStates(StatesGroup):
    waiting_request = State()


# Строка вида "1 текст", "1. текст", "1) текст", "1: текст"
NUMBERED_LINE_RE = re.compile(r"^\s*([1-4])[\.\)\:]?\s+(.*\S)?\s*$")

POSITIVE_WORDS = {"да", "нужно", "yes", "надо", "необходимо", "конечно", "+", "хочу"}

INSTRUCTIONS_TEXT = (
    "Введите ваш запрос, после которого я могу отправить данные для генерации поста "
    "с указаниями через цифры:\n"
    "1 Пример поста\n"
    "2 Надо ли проводить поиск информации в интернете для дополнения\n"
    "3 Сохранить ли стиль оригинала\n"
    "4 Дополнительные заметки\n\n"
    "Любой из пунктов можно пропустить — это не помешает обработке остальных."
)


async def _delete_previous(message: Message) -> None:
    last_id = storage.get_last_message(message.chat.id)
    if last_id:
        try:
            await message.bot.delete_message(message.chat.id, last_id)
        except Exception:
            pass
        storage.clear_last_message(message.chat.id)


def parse_request(text: str) -> dict:
    """Разбирает сообщение на основной текст запроса и пункты 1-4.

    Отсутствие любого из пунктов не мешает разбору остальных —
    просто соответствующее поле остаётся пустым.
    """
    fields: dict[int, str] = {}
    main_lines = []

    for line in text.splitlines():
        match = NUMBERED_LINE_RE.match(line)
        if match:
            num = int(match.group(1))
            fields[num] = (match.group(2) or "").strip()
        elif line.strip():
            main_lines.append(line.strip())

    return {
        "main_text": "\n".join(main_lines).strip(),
        "example_post": fields.get(1, "").strip(),
        "need_search_raw": fields.get(2, "").strip(),
        "keep_style_raw": fields.get(3, "").strip(),
        "notes": fields.get(4, "").strip(),
    }


def _is_positive(value: str) -> bool:
    value_low = value.lower()
    return any(word in value_low for word in POSITIVE_WORDS)


@router.message(F.text == "Content")
async def on_content_button(message: Message, state: FSMContext) -> None:
    await _delete_previous(message)
    sent = await message.answer(INSTRUCTIONS_TEXT)
    storage.set_last_message(message.chat.id, sent.message_id)
    await state.set_state(ContentStates.waiting_request)


@router.message(ContentStates.waiting_request)
async def on_content_request(message: Message, state: FSMContext) -> None:
    await _delete_previous(message)

    parsed = parse_request(message.text or "")

    search_context = ""
    if parsed["need_search_raw"] and _is_positive(parsed["need_search_raw"]):
        query = parsed["main_text"] or parsed["notes"] or (message.text or "")
        try:
            search_context = await web_search(query)
        except Exception as e:
            search_context = f"(поиск не удался: {e})"

    keep_style = True
    if parsed["keep_style_raw"]:
        keep_style = _is_positive(parsed["keep_style_raw"]) or "сохран" in parsed["keep_style_raw"].lower()

    prompt_parts = [f"Запрос пользователя: {parsed['main_text'] or message.text}"]

    if parsed["example_post"]:
        prompt_parts.append(f"Пример поста для ориентира:\n{parsed['example_post']}")
        prompt_parts.append(
            "Сохраняй стиль, тон и структуру примера."
            if keep_style
            else "Пример дан только для контекста, стиль можно менять свободно."
        )

    if search_context:
        prompt_parts.append(f"Дополнительная информация из интернета:\n{search_context}")

    if parsed["notes"]:
        prompt_parts.append(f"Дополнительные заметки: {parsed['notes']}")

    prompt = "\n\n".join(prompt_parts)

    waiting = await message.answer("Генерирую пост, подождите…")
    storage.set_last_message(message.chat.id, waiting.message_id)

    try:
        result = await generate_post(prompt)
    except Exception as e:
        result = f"Ошибка генерации: {e}"

    await _delete_previous(message)
    sent = await message.answer(result, reply_markup=main_menu_kb())
    storage.set_last_message(message.chat.id, sent.message_id)
    await state.clear()
