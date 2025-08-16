import re

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.db.database import *
from bot.models.movie_data import DisplayableMovie
from bot.utils.list_utils import edit_movie_list
from bot.services.movies_api import find_movies_by_title, get_details_by_id
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

    if message_context.mode == MessageMode.SEARCH:
        movies, _, total = await get_search_data(message_id, user_id)
    elif message_context == MessageMode.HISTORY:
        movies, total = await get_history_data(user_id, message_context.page)
    else:
        movies, total = await get_stats_data(user_id, message_context.page)

    if not movies or idx >= len(movies):
        await callback_query.answer("Фильм не найден.")
        return

    movie: 'DisplayableMovie' = movies[idx]

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

    direction = -1 if callback_query.data == "left_arrow" else 1

    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id
    message_context = await load_message_context(message_id, user_id)

    message_context.page += direction

    if message_context.mode == MessageMode.HISTORY:
        movies, total = await get_history_data(user_id, message_context.page)
    elif message_context.mode == MessageMode.SEARCH:
        old_movies, query_title, total = await get_search_data(message_id, user_id)
        movies, total = await find_movies_by_title(query_title, message_context.page)
        await save_search_data(message_id, user_id, query_title, movies, total)
    else:
        movies, total = await get_stats_data(user_id, message_context.page)

    logger.info(f"New page {message_context.page} of movies: {movies}")

    await edit_movie_list(callback_query.message, movies, total, message_context)

@router.callback_query(F.data.regexp(r"(h?)return$"))
async def process_callback_return(callback_query: CallbackQuery):
    logger.info(f'{callback_query.data} pressed! From message: {callback_query.message.message_id}')

    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id
    message_context = await load_message_context(message_id, user_id)

    message_context.page = 1

    if message_context.mode == MessageMode.HISTORY:
        movies, total = await get_history_data(user_id, message_context.page)
    elif message_context.mode == MessageMode.SEARCH:
        old_movies, query_title, total = await get_search_data(message_id, user_id)
        movies, total = await find_movies_by_title(query_title, message_context.page)
        await save_search_data(message_id, user_id, query_title, movies, total)
    else:
        movies, total = await get_stats_data(user_id, message_context.page)

    logger.info(f"New page {message_context.page} of movies: {movies}")

    await edit_movie_list(callback_query.message, movies, total, message_context)
