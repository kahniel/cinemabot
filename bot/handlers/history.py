from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.db.database import get_history_data
from bot.utils.list_utils import send_movie_list
from bot.models.message_data import MessageContext, MessageMode
from emoji import emojize

import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("history"))
async def cmd_history(message: Message):
    movies, total = await get_history_data(message.from_user.id)

    if not total:
        text = emojize(
            ":open_mailbox_with_lowered_flag: Ты ещё ничего не искал. Начни с любого фильма — я всё запомню!"
        )
        await message.answer(text)
        return

    message_context = MessageContext(page=1, mode=MessageMode.HISTORY)

    logger.info(f"Movies in history: {movies}")

    await send_movie_list(message, movies, total, message_context)
