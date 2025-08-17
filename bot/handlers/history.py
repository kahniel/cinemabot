from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.db.database import get_history_data
from bot.models.message_data import MessageContext
from bot.utils.list_utils import send_movie_list
from emoji import emojize

import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("history"))
async def cmd_history(message: Message):
    message_context: 'MessageContext' = await get_history_data(message.from_user.id)

    if not message_context.total:
        text = emojize(
            ":open_mailbox_with_lowered_flag: Ты ещё ничего не искал. Начни с любого фильма — я всё запомню!"
        )
        await message.answer(text)
        return

    logger.info(f"Movies in history: {message_context.movies}")

    await send_movie_list(message, message_context)
