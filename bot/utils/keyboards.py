from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.services.movies_api import MOVIES_ON_PAGE
from emoji import emojize
import logging

logger = logging.getLogger(__name__)

def generate_selector_kb(total: int, page: int) -> InlineKeyboardMarkup:
    pages_num = (total + MOVIES_ON_PAGE - 1) // MOVIES_ON_PAGE
    movies_left = total - (page - 1) * MOVIES_ON_PAGE

    num_buttons = []
    for i in range(0, min(MOVIES_ON_PAGE, movies_left)):
        button = InlineKeyboardButton(
            text=f"{i + 1}️", callback_data=f"button{i + 1}"
        )
        num_buttons.append(button)

    action_buttons = []
    if page != 1:
        button = InlineKeyboardButton(
            text=emojize(":left_arrow:"), callback_data=f"left_arrow"
        )
        action_buttons.append(button)

    action_buttons.append(InlineKeyboardButton(
        text=f"{page}/{pages_num}", callback_data=f"return"
    ))

    if page < pages_num:
        button = InlineKeyboardButton(
            text=emojize(":right_arrow:"), callback_data=f"right_arrow"
        )
        action_buttons.append(button)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            num_buttons[:MOVIES_ON_PAGE//2],
            num_buttons[MOVIES_ON_PAGE//2:],
            action_buttons
        ]
    )
    return kb
