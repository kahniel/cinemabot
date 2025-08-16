import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot import config
from bot.handlers import start, help as help_cmd, search, history, stats
from bot.utils import selector

from bot.db.database import init_db

import logging
from bot.logging_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(help_cmd.router)
    dp.include_router(search.router)
    dp.include_router(history.router)
    dp.include_router(stats.router)
    dp.include_router(selector.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
