import html
from dataclasses import dataclass, asdict
from typing import Optional

from aiogram.types import Message, LinkPreviewOptions, InlineKeyboardButton, InlineKeyboardMarkup

from emoji import emojize
import logging

logger = logging.getLogger(__name__)

@dataclass
class MovieShort:
    id: int
    title: str
    year: Optional[int] = None
    count: Optional[int] = None


    def __post_init__(self):
        if not isinstance(self.id, int) or self.id <= 0:
            raise ValueError("ID is supposed to be integer >= 0")
        if not self.title or not self.title.strip():
            raise ValueError("Movie title cannot be empty")
        if self.year is not None and (not isinstance(self.year, int) or self.year < 1800 or self.year > 2030):
            self.year = None
        if self.count is not None and (not isinstance(self.count, int) or self.count < 0):
            raise ValueError("Count is supposed to be integer >= 0")

    def to_dict(self) -> dict:
        return asdict(self) # type: ignore

    @classmethod
    def from_dict(cls, dct: dict) -> 'MovieShort':
        return cls(**dct)

@dataclass
class Platform:
    name: str
    url: str

@dataclass
class MovieDetails:
    id: int
    title: str
    watchability: list['Platform']
    year: Optional[int] = None
    rating: Optional[float] = None
    plot: Optional[str] = None
    poster_url: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.id, int) or self.id <= 0:
            raise ValueError("ID is supposed to be integer >= 0")
        if not self.title or not self.title.strip():
            raise ValueError("Movie title cannot be empty")
        if self.year is not None and (not isinstance(self.year, int) or self.year < 1800 or self.year > 2030):
            raise ValueError("Year is supposed to be between 1800 and 2030")
        if self.rating is not None and (not isinstance(self.rating, (int, float)) or self.rating < 0 or self.rating > 10):
            raise ValueError("Rating is supposed to be between 0 and 10")

    def has_complete_info(self) -> bool:
        return all([
            self.year is not None,
            self.rating is not None,
            self.plot is not None and self.plot.strip(),
            self.poster_url is not None and self.poster_url.strip()
        ])

    def to_short(self) -> MovieShort:
        return MovieShort(id=self.id, title=self.title, year=self.year)

    def generate_text(self):
        safe_title = html.escape(self.title)

        text = f":clapper_board: <b>{safe_title}</b> ({self.year})\n"

        if self.rating != 0:
            text += f":star: <b>Рейтинг:</b> {self.rating}/10\n\n"

        if self.plot:
            clean_plot = self.plot.replace('\xa0', ' ').replace('\u00a0', ' ').strip()
            safe_plot = html.escape(clean_plot)

            text += f":memo: <b>Описание:</b> {safe_plot}\n\n"

        return emojize(text)

    def generate_platforms_kb(self):
        keyboard = []
        for platform in self.watchability:
            keyboard.append([
                InlineKeyboardButton(
                    text=platform.name,
                    url=platform.url
                )
            ])
        if not keyboard:
            keyboard.append([
                InlineKeyboardButton(
                    text=emojize(":magnifying_glass_tilted_right: Найти онлайн"),
                    url=f"https://www.google.com/search?q={self.title.replace(' ', '+')}+смотреть+онлайн"
                )
            ])


        logger.info(f"Buttons: {keyboard}")

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    async def send(self, message: Message):
        caption = self.generate_text()
        if self.poster_url:
            try:
                if len(caption) <= 1020:
                    await message.answer_photo(
                        photo=self.poster_url,
                        caption=self.generate_text(),
                        parse_mode="HTML",
                        reply_markup=self.generate_platforms_kb()
                    )
                    return
                else:
                    await message.answer_photo(
                        photo=self.poster_url
                    )
            except Exception as e:
                logger.warning(f"Failed to send photo {self.poster_url}: {e}")

        await message.answer(
            text=caption,
            parse_mode="HTML",
            link_preview_options=LinkPreviewOptions(is_disabled=True),
            reply_markup=self.generate_platforms_kb()
        )
