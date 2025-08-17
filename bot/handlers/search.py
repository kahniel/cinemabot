import aiohttp
from aiogram import Router, F
from aiogram.types import Message
from emoji import emojize

from bot.utils.list_utils import send_movie_list
from bot.services.movies_api import find_movies_by_title
from bot.models.message_data import MessageContext, MessageMode
from bot.db.database import save_search_cache
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(F.text & ~F.text.startswith("/"))
async def search_movie(message: Message) -> None:
    query_title = message.text.strip()

    logger.info(f"searching: {query_title}")
    try:
        message_context = await find_movies_by_title(query_title)
    except aiohttp.ClientResponseError as e:
        text = emojize(f":no_entry: Ошибка при поиске фильма (код {e.status}). Попробуй снова.")
        await message.answer(text=text)
        return

    if not message_context.total:
        text = emojize(":disappointed_face: Фильмы не найдены, проверь название.")
        await message.answer(text=text)
        return

    msg = await send_movie_list(message, message_context)
    await save_search_cache(
        message_id=msg.message_id,
        user_id=message.from_user.id,
        query_title=query_title
    )
