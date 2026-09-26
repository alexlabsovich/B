import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
from handlers import channels, common, content
from services.telethon_client import start_userbot, stop_userbot, update_all_channels

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(common.router)
    dp.include_router(content.router)
    dp.include_router(channels.router)

    # Юзербот-аккаунт, который админ во всех отслеживаемых каналах
    await start_userbot()

    # Раз в сутки обновляем данные по каналам (подписчики, просмотры и т.д.)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_all_channels, "interval", hours=24)
    scheduler.start()

    try:
        await dp.start_polling(bot)
    finally:
        await stop_userbot()


if __name__ == "__main__":
    asyncio.run(main())
