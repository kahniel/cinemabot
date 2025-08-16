from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.db.database import get_stats_data
from bot.models.message_data import MessageContext, MessageMode
from emoji import emojize

import logging

from bot.utils.list_utils import send_movie_list

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    movies, total = await get_stats_data(message.from_user.id)

    if not total:
        text = emojize(
            ":chart_decreasing: У тебя пока нет статистики. Начни с поиска фильма!"
        )
        await message.answer(text)
        return

    message_context = MessageContext(page=1, mode=MessageMode.STATS)

    await send_movie_list(message, movies, total, message_context)
