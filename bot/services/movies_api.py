import aiohttp

from bot.models.message_data import MessageContext, MessageMode
from bot.models.movie_data import MovieShort, MovieDetails, Platform
from bot.config import KP_API_KEY
import logging

logger = logging.getLogger(__name__)

MOVIES_ON_PAGE = 8

BASE_SEARCH_URL = "https://api.kinopoisk.dev/v1.4/movie/search"
BASE_MOVIE_URL = "https://api.kinopoisk.dev/v1.4/movie"

HEADERS = {
    "accept": "application/json",
    "X-API-KEY": KP_API_KEY
}

def select_rating(unparsed_details: dict) -> int:
    rating = unparsed_details.get("rating")
    votes = unparsed_details.get("votes")
    rating_votes = [(votes[key], rating[key])  for key in rating.keys()]
    return max(rating_votes)[1]

def parse_movie_details(unparsed_details: dict) -> MovieDetails:
    if unparsed_details.get("title"):
        title = unparsed_details.get("title")
    elif unparsed_details.get("name"):
        title = unparsed_details.get("name")
    else:
        title = unparsed_details.get("alternativeName")
    logger.info(f"Chosen title: {title}")

    watchability = []
    if unparsed_details.get("watchability").get("items"):
        for item in unparsed_details.get("watchability").get("items"):
            watchability.append(
                Platform(
                    name=item.get('name'),
                    url=item.get('url')
                )
            )

    return MovieDetails(
        id=unparsed_details.get('id'),
        title=title,
        watchability=watchability,
        year=unparsed_details.get("year"),
        rating = select_rating(unparsed_details),
        plot=unparsed_details.get("description"),
        poster_url=unparsed_details.get("poster").get("url") if unparsed_details.get("poster") else None
    )

async def get_details_by_id(item_id: int) -> MovieDetails | None:
    async with aiohttp.ClientSession() as session:
        detail_url = f"{BASE_MOVIE_URL}/{item_id}"
        async with session.get(detail_url, headers=HEADERS) as response:
            if response.status != 200:
                return None
            unparsed_details = await response.json()

            return parse_movie_details(unparsed_details)

async def find_movies_by_title(query_title: str, page: int = 1) -> 'MessageContext':
    params = {
        "query": query_title,
        "page" : f"{page}",
        "limit" : f"{MOVIES_ON_PAGE}"
    }

    async with (aiohttp.ClientSession() as session):
        async with session.get(BASE_SEARCH_URL, headers=HEADERS, params=params) as response:
            data = await response.json()
            if response.status != 200:
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=data.get('message')
                )
            parsed_movies =[]
            for movie in data.get("docs"):
                parsed_movies.append(
                    MovieShort(
                        title=movie.get("name") if movie.get("name") else movie.get("alternativeName"),
                        year=movie.get("year"),
                        id=movie.get("id")
                    )
                )
            return MessageContext(
                page=page,
                mode=MessageMode.SEARCH,
                total=data.get("total"),
                movies=parsed_movies
            )

