from dataclasses import dataclass
from enum import Enum
from bot.models.movie_data import MovieShort

import logging

from bot.config import MOVIES_ON_PAGE

logger = logging.getLogger(__name__)

class MessageMode(Enum):
    SEARCH = 'search'
    HISTORY = 'history'
    STATS = 'stats'

@dataclass
class MessageContext:
    page: int
    mode: MessageMode
    total: int
    movies: list['MovieShort']

    @property
    def pages_num(self):
        return (self.total + MOVIES_ON_PAGE - 1) // MOVIES_ON_PAGE

    @property
    def movies_left(self):
        return self.total - (self.page - 1) * MOVIES_ON_PAGE

    def __post_init__(self):
        if self.page < 1:
            raise ValueError("Страница должна быть больше 0")
