import json
from dataclasses import asdict

import aiosqlite
import os
import logging

from bot.models.movie_data import DisplayableMovie
from bot.models.movie_data import MovieShort, MovieStat
from bot.models.message_data import MessageContext, MessageMode
from bot.services.movies_api import MOVIES_ON_PAGE

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "cinema.db")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                movie_id INTEGER NOT NULL,
                movie_title TEXT NOT NULL,
                movie_year INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                user_id INTEGER,
                movie_id INTEGER NOT NULL,
                movie_title TEXT NOT NULL,
                movie_year INTEGER,
                count INTEGER DEFAULT 1,
                PRIMARY KEY (user_id, movie_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS message_context (
                message_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                mode TEXT NOT NULL,  -- 'search', 'history', 'stats'
                page INTEGER DEFAULT 1,
                PRIMARY KEY (message_id, user_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS search_cache (
                message_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                query_title TEXT NOT NULL,
                total INTEGER NOT NULL,
                movies_json TEXT NOT NULL,  -- JSON с массивом объектов MovieShort
                PRIMARY KEY (message_id, user_id),
                FOREIGN KEY (message_id, user_id)
                    REFERENCES message_context(message_id, user_id)
                    ON DELETE CASCADE
            )
        """)
        await db.commit()


async def add_movie_to_history(user_id: int, movie: 'DisplayableMovie'):
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute("""
                INSERT INTO history (user_id, movie_id, movie_title, movie_year)
                VALUES (?, ?, ?, ?)
            """, (user_id, movie.id, movie.title, movie.year))

            await db.execute("""
                INSERT INTO stats (user_id, movie_id, movie_title, movie_year, count)
                VALUES (?, ?, ?, ?, 1)
                ON CONFLICT(user_id, movie_id) DO UPDATE SET count = count + 1
            """, (user_id, movie.id, movie.title, movie.year))

            await db.commit()
        except Exception:
            await db.rollback()
            raise


async def get_history_data(user_id: int, page: int = 1) -> tuple[list['MovieShort'], int]:
    offset = (page - 1) * MOVIES_ON_PAGE

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT movie_id, movie_title, movie_year 
            FROM history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, MOVIES_ON_PAGE, offset))

        rows = await cursor.fetchall()
        movies = [MovieShort(id=row[0], title=row[1], year=row[2]) for row in rows]

        cursor_total = await db.execute("SELECT COUNT(*) FROM history WHERE user_id = ?", (user_id,))
        total = (await cursor_total.fetchone())[0]

        return movies, total


async def get_stats_data(user_id: int, page: int = 1) -> tuple[list['MovieStat'], int]:
    offset = (page - 1) * MOVIES_ON_PAGE

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
                SELECT movie_id, movie_title, movie_year, count
                FROM stats
                WHERE user_id = ?
                ORDER BY count DESC
                LIMIT ? OFFSET ?
            """, (user_id, MOVIES_ON_PAGE, offset))

        rows = await cursor.fetchall()
        movies = [
            MovieStat(
                movie=MovieShort(id=row[0], title=row[1], year=row[2]),
                count=row[3]
            )
            for row in rows
        ]

        cursor_total = await db.execute("SELECT COUNT(*) FROM stats WHERE user_id = ?", (user_id,))
        total = (await cursor_total.fetchone())[0]

        return movies, total


async def get_search_data(message_id: int, user_id: int) -> tuple[list['MovieShort'], str, int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT movies_json, query_title, total
            FROM search_cache
            WHERE message_id = ? AND user_id = ?
        """, (message_id, user_id))

        row = await cursor.fetchone()
        if not row:
            raise ValueError('Search cache not found')

        movies_json, query_title, total = row
        movies = [MovieShort(**movie) for movie in json.loads(movies_json)]

        return movies, query_title, total

async def save_search_data(
        message_id: int,
        user_id: int,
        query_title: str,
        movies: list['MovieShort'],
        total: int
    ) -> None:

    async with aiosqlite.connect(DB_PATH) as db:
        movies_json = json.dumps([asdict(movie) for movie in movies], ensure_ascii=False) # type: ignore

        await db.execute("""
            INSERT OR REPLACE INTO search_cache
            (message_id, user_id, query_title, total, movies_json)
            VALUES (?, ?, ?, ?, ?)
        """, (message_id, user_id, query_title, total, movies_json))

        await db.commit()

async def save_message_context(
        message_id: int,
        user_id: int,
        message_context: MessageContext,
    ) -> None:

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO message_context
            (message_id, user_id, mode, page)
            VALUES (?, ?, ?, ?)
        """, (
                message_id, user_id, message_context.mode.value, message_context.page
            )
        )

        await db.commit()


async def load_message_context(message_id: int, user_id: int) -> MessageContext:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT mode, page
            FROM message_context 
            WHERE message_id = ? AND user_id = ?
        """, (message_id, user_id))
        row = await cursor.fetchone()

        if not row:
            raise ValueError('Message context not found')

        mode_str, page = row
        mode = MessageMode(mode_str)

        return MessageContext(
            page=page,
            mode=mode
        )
