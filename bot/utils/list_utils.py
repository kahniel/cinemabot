from aiogram.types import Message
from bot.db.database import save_message_context, save_search_cache, get_stats_data, get_history_data, get_search_cache
from bot.models.message_data import MessageContext, MessageMode
from bot.config import MOVIES_ON_PAGE
from bot.services.movies_api import find_movies_by_title

from bot.utils.keyboards import generate_selector_kb
from emoji import emojize
import logging

logger = logging.getLogger(__name__)

HEADERS = {
    MessageMode.HISTORY: ":scroll: <b>Твоя история:</b>\n\n",
    MessageMode.SEARCH: ":clapper_board: <b>Найдено по твоему запросу:</b>\n\n",
    MessageMode.STATS: ":bar_chart: <b>Твоя статистика:</b>\n\n"
}

def generate_list_text(message_context: MessageContext) -> str:
    logger.info(f"To display: {message_context.movies_left}|{len(message_context.movies)} movies")

    text = HEADERS[message_context.mode]

    for i, movie in enumerate(message_context.movies[:min(MOVIES_ON_PAGE, message_context.movies_left)]):
        text += f"{i + 1}. <b>{movie.title}</b>"
        if movie.year is not None:
            text += f" ({movie.year})"
        if message_context.mode == MessageMode.STATS and movie.count is not None:
            text += f" — <i>{getattr(movie, 'count', 0)}</i> раз(а)"
        text += "\n"

    return emojize(text)

async def send_movie_list(message: Message, message_context: MessageContext) -> 'Message':
    text = generate_list_text(message_context)

    msg = await message.answer(
        text=text,
        reply_markup=generate_selector_kb(message_context),
        parse_mode="HTML"
    )
    logger.info(f"Sending to db: message_id: {msg.message_id}")
    await save_message_context(
        message_id=msg.message_id,
        user_id=message.from_user.id,
        message_context=message_context
    )
    return msg


async def edit_movie_list(message: Message, message_context: MessageContext) -> None:
    text = generate_list_text(message_context)

    await message.edit_text(
        text=text,
        reply_markup=generate_selector_kb(message_context),
        parse_mode="HTML"
    )

    logger.info(f"Editing db: uid, mid: [{message.from_user.id}, {message.message_id}], page: {message_context.page}")
    await save_message_context(
        message_id=message.message_id,
        user_id=message.from_user.id,
        message_context=message_context
    )

async def update_page(message_context: MessageContext, message_id: int, user_id: int, new_page: int) -> None:
    message_context.page = new_page

    if message_context.mode == MessageMode.HISTORY:
        ctx = await get_history_data(user_id, message_context.page)
    elif message_context.mode == MessageMode.SEARCH:
        query_title = await get_search_cache(message_id, user_id)
        ctx = await find_movies_by_title(query_title, message_context.page)
        await save_search_cache(message_id, user_id, query_title)
    else:  # stats
        ctx = await get_stats_data(user_id, message_context.page)
    message_context.movies = ctx.movies
    message_context.total = ctx.total

    await save_message_context(message_id, user_id, message_context)

    logger.info(f"Updated page {message_context.page} of movies: {message_context.movies}")
