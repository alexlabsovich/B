import json
import os
from typing import Any, Optional

import config


def _load(path: str, default: Any):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(path: str, data: Any):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_channels_data() -> list:
    """Кэш данных по каналам: подписчики, просмотры, аватар, ссылка и т.д."""
    return _load(config.CHANNELS_FILE, [])


def save_channels_data(data: list):
    _save(config.CHANNELS_FILE, data)


def load_tracked_channels() -> list:
    """Список username/id каналов, которые нужно отслеживать."""
    return _load(config.TRACKED_CHANNELS_FILE, [])


def save_tracked_channels(data: list):
    _save(config.TRACKED_CHANNELS_FILE, data)


# --- Последнее сообщение бота в чате (чтобы удалять его при новом запросе) ---

_last_bot_message: dict[int, int] = {}


def set_last_message(chat_id: int, message_id: int) -> None:
    _last_bot_message[chat_id] = message_id


def get_last_message(chat_id: int) -> Optional[int]:
    return _last_bot_message.get(chat_id)


def clear_last_message(chat_id: int) -> None:
    _last_bot_message.pop(chat_id, None)
