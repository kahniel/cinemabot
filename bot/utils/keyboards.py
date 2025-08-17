from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.models.message_data import MessageContext
from bot.config import MOVIES_ON_PAGE
from emoji import emojize
import logging

logger = logging.getLogger(__name__)

def generate_selector_kb(message_context: MessageContext) -> InlineKeyboardMarkup:
    num_buttons = []
    for i in range(0, min(MOVIES_ON_PAGE, message_context.movies_left)):
        button = InlineKeyboardButton(
            text=f"{i + 1}️", callback_data=f"button{i + 1}"
        )
        num_buttons.append(button)

    action_buttons = []
    if message_context.page != 1:
        button = InlineKeyboardButton(
            text=emojize(":left_arrow:"), callback_data=f"left_arrow"
        )
        action_buttons.append(button)

    action_buttons.append(InlineKeyboardButton(
        text=f"{message_context.page}/{message_context.pages_num}", callback_data=f"return"
    ))

    if message_context.page < message_context.pages_num:
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
