from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from emoji import emojize

router = Router()

@router.message(Command("help"))
async def cmd_help(message: Message):
    text = emojize(
        ":old_key: <b>Что я умею:</b>\n\n"
        ":magnifying_glass_tilted_right: Пришли название фильма или сериала — я найду инфу и подскажу, где его смотреть.\n\n"
        ":scroll: /history — последние 10 твоих запросов\n"
        ":bar_chart: /stats — что ты искал чаще всего\n\n"
        "Попробуй написать, например: <i>Джокер</i>, <i>Бойцовский клуб</i>, <i>Тьма</i>"
    )
    await message.answer(text=text, parse_mode="HTML")