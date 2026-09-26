import os
from datetime import datetime, timezone
from typing import Optional

from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import ExportChatInviteRequest

import config
import storage

_client: Optional[TelegramClient] = None


async def start_userbot() -> None:
    """Запускает Telethon-клиент под аккаунтом-администратором каналов.

    При первом запуске Telethon попросит номер телефона и код подтверждения
    прямо в консоли — это нормально, так создаётся файл сессии
    (config.TELEGRAM_SESSION_NAME + '.session'), при следующих запусках
    авторизация уже не потребуется.
    """
    global _client
    os.makedirs(config.AVATARS_DIR, exist_ok=True)
    _client = TelegramClient(
        config.TELEGRAM_SESSION_NAME,
        config.TELEGRAM_API_ID,
        config.TELEGRAM_API_HASH,
    )
    await _client.start()


async def stop_userbot() -> None:
    if _client:
        await _client.disconnect()


async def add_tracked_channel(username_or_id: str) -> dict:
    tracked = storage.load_tracked_channels()
    if username_or_id not in tracked:
        tracked.append(username_or_id)
        storage.save_tracked_channels(tracked)
    return await update_channel(username_or_id)


async def remove_tracked_channel(username_or_id: str) -> None:
    tracked = storage.load_tracked_channels()
    tracked = [c for c in tracked if c != username_or_id]
    storage.save_tracked_channels(tracked)


async def _get_invite_link(channel) -> str:
    if getattr(channel, "username", None):
        return f"https://t.me/{channel.username}"
    try:
        result = await _client(ExportChatInviteRequest(channel))
        return result.link
    except Exception:
        return ""


async def update_channel(username_or_id: str) -> dict:
    """Забирает свежие данные по одному каналу: подписчики, просмотры
    последнего поста, аватар, ссылку — и сохраняет в кэш."""
    entity = await _client.get_entity(username_or_id)
    full = await _client(GetFullChannelRequest(entity))

    subscribers = full.full_chat.participants_count or 0

    last_views = 0
    async for msg in _client.iter_messages(entity, limit=1):
        last_views = msg.views or 0

    avatar_path = os.path.join(config.AVATARS_DIR, f"{entity.id}.jpg")
    try:
        downloaded = await _client.download_profile_photo(entity, file=avatar_path)
        if not downloaded:
            avatar_path = ""
    except Exception:
        avatar_path = ""

    link = await _get_invite_link(entity)

    info = {
        "id": entity.id,
        "title": entity.title,
        "username": getattr(entity, "username", None),
        "link": link,
        "subscribers": subscribers,
        "last_post_views": last_views,
        "avatar_path": avatar_path,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    data = storage.load_channels_data()
    data = [c for c in data if c.get("id") != info["id"]]
    data.append(info)
    storage.save_channels_data(data)

    return info


async def update_all_channels() -> None:
    """Ежедневное обновление данных по всем отслеживаемым каналам."""
    tracked = storage.load_tracked_channels()
    for ch in tracked:
        try:
            await update_channel(ch)
        except Exception as e:
            print(f"[telethon_client] Не удалось обновить канал {ch}: {e}")
