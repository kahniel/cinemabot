from dataclasses import dataclass
from enum import Enum
from bot.models.movie_data import MovieShort

import logging

logger = logging.getLogger(__name__)

class MessageMode(Enum):
    SEARCH = 'search'
    HISTORY = 'history'
    STATS = 'stats'

@dataclass
class MessageContext:
    page: int
    mode: MessageMode

    def __post_init__(self):
        if self.page < 1:
            raise ValueError("Страница должна быть больше 0")

@dataclass
class SearchContext:
    movies: list['MovieShort']
    query_title: str
    total: int
