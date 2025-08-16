from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from emoji import emojize

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    text = emojize(
        f":waving_hand: Привет, <b>{message.from_user.full_name}</b>!\n\n"
        f"Я — ioMoviesBot. Помогу найти фильмы и сериалы: описание, рейтинг, постер и где посмотреть.\n\n"
        f"Просто пришли мне название — и магия начнётся :sparkles:\n\n"
        f"Напиши /help, чтобы узнать больше."
    )
    await message.answer(text=text, parse_mode="HTML")
