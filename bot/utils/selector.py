import re

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.db.database import *
from bot.utils.list_utils import edit_movie_list, update_page
from bot.services.movies_api import get_details_by_id
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(F.data.regexp(r"button(\d+)$"))
async def process_callback_button_num(callback_query: CallbackQuery):
    logger.info(f'{callback_query.data} pressed! From message: {callback_query.message.message_id}')
    idx = int(re.match(r"button(\d+)$", callback_query.data).group(1)) - 1

    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id
    message_context = await load_message_context(message_id, user_id)

    movie = message_context.movies[idx]

    logger.info(f"Looking for movie: {movie.id}")
    movie_details = await get_details_by_id(movie.id)
    logger.info(f"Found: {movie_details}")

    await add_movie_to_history(
        user_id=callback_query.from_user.id,
        movie=movie
    )
    await movie_details.send(callback_query.message)

@router.callback_query(F.data.regexp(r"(h?)(left|right)_arrow$"))
async def process_callback_arrow(callback_query: CallbackQuery):
    logger.info(f'{callback_query.data} pressed! From message: {callback_query.message.message_id}')

    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id
    message_context = await load_message_context(message_id, user_id)

    new_page = message_context.page + (-1 if callback_query.data == "left_arrow" else 1)

    await update_page(message_context, message_id, user_id, new_page)

    await edit_movie_list(callback_query.message, message_context)

@router.callback_query(F.data.regexp(r"(h?)return$"))
async def process_callback_return(callback_query: CallbackQuery):
    logger.info(f'{callback_query.data} pressed! From message: {callback_query.message.message_id}')

    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id
    message_context = await load_message_context(message_id, user_id)

    await update_page(message_context, message_id, user_id, 1)

    await edit_movie_list(callback_query.message, message_context)
