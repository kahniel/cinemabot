from aiogram.types import Message
from bot.db.database import save_message_context
from bot.models.message_data import MessageContext, MessageMode
from bot.models.movie_data import DisplayableMovie
from bot.services.movies_api import MOVIES_ON_PAGE

from bot.utils.keyboards import generate_selector_kb
from emoji import emojize
import logging

logger = logging.getLogger(__name__)

HEADERS = {
    MessageMode.HISTORY: ":scroll: <b>Твоя история:</b>\n\n",
    MessageMode.SEARCH: ":clapper_board: <b>Найдено по твоему запросу:</b>\n\n",
    MessageMode.STATS: ":bar_chart: <b>Твоя статистика:</b>\n\n"
}

def generate_list_text(movies: list['DisplayableMovie'], total: int, message_context: MessageContext) -> str:
    movies_left = total - (message_context.page - 1) * MOVIES_ON_PAGE
    logger.info(f"To display: {movies_left}|{len(movies)} movies")

    text = HEADERS[message_context.mode]

    for i, movie in enumerate(movies[:min(MOVIES_ON_PAGE, movies_left)]):
        text += f"{i + 1}. <b>{movie.title}</b>"
        if movie.year is not None:
            text += f" ({movie.year})"
        if message_context.mode == MessageMode.STATS and movie.count is not None:
            text += f" — <i>{getattr(movie, 'count', 0)}</i> раз(а)"
        text += "\n"

    return emojize(text)

async def send_movie_list(
        message: Message,
        movies: list['DisplayableMovie'], total: int, message_context: MessageContext
    ) -> 'Message':

    text = generate_list_text(movies, total, message_context)

    msg = await message.answer(
        text=text,
        reply_markup=generate_selector_kb(
            total,
            message_context.page
        ),
        parse_mode="HTML"
    )
    logger.info(f"Sending to db: message_id: {msg.message_id}")
    await save_message_context(
        message_id=msg.message_id,
        user_id=message.from_user.id,
        message_context=message_context
    )
    return msg


async def edit_movie_list(
        message: Message,
        movies: list['DisplayableMovie'], total: int, message_context: MessageContext
    ) -> None:

    text = generate_list_text(movies, total, message_context)

    await message.edit_text(
        text=text,
        reply_markup=generate_selector_kb(
            total,
            message_context.page
        ),
        parse_mode="HTML"
    )

    logger.info(f"Editing db: uid, mid: [{message.from_user.id}, {message.message_id}], page: {message_context.page}")
    await save_message_context(
        message_id=message.message_id,
        user_id=message.from_user.id,
        message_context=message_context
    )
