from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.db.database import get_stats_data
from bot.models.message_data import MessageContext
from emoji import emojize

import logging

from bot.utils.list_utils import send_movie_list

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    message_context: 'MessageContext' = await get_stats_data(message.from_user.id)

    if not message_context.total:
        text = emojize(
            ":chart_decreasing: У тебя пока нет статистики. Начни с поиска фильма!"
        )
        await message.answer(text)
        return

    await send_movie_list(message, message_context)
