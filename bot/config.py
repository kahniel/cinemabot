import os
import dotenv

dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

KP_API_KEY = os.getenv("KP_API_KEY")

if not KP_API_KEY:
    raise RuntimeError("KP_API_KEY is not set")

MOVIES_ON_PAGE = 8