import os
import random
from datetime import datetime, date
import pytz
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError
from requests.exceptions import RequestException

from PIL import Image
from .config import ASSETS_DIR

# ================= WIKIPEDIA =================

def search_wikipedia(query: str) -> str | None:
    try:
        wikipedia.set_lang("en")
        page = wikipedia.page(query, auto_suggest=False)
        if query.lower() not in page.title.lower():
            return None
        summary = wikipedia.summary(
            page.title,
            sentences=5,
            auto_suggest=False,)
        if len(summary) > 1000:
            summary = summary[:997].rstrip() + "..."
        return summary
    except (DisambiguationError, PageError, RequestException):
        return None

# ================= IMAGES =================

def get_random_image():
    image_names = [ "116.jpg", "117.jpg", "118.jpg", "119.webp", "120.jpg",
        "121.webp", "122.jpg", "123.png", "124.png", "125.webp",
        "126.webp", "127.png", "128.jpg", "129.jpg", "130.jpg",
        "131.jpg", "132.png", "133.png", "134.png", "135.png", "136.png"]

    path = os.path.join(ASSETS_DIR, random.choice(image_names))
    return Image.open(path)

def get_wiki_image():
    return Image.open(os.path.join(ASSETS_DIR, "wiki.jpg"))

# ================= TIME & DATE =================

def get_ny_time() -> str:
    ny_time = datetime.now(pytz.timezone("America/New_York"))
    return ny_time.strftime('%H:%M:%S')


def get_current_date() -> str:
    return date.today().strftime('%d-%m-%Y')

# ================= FALLBACK =================

def random_fallback_sticker(stickers: list[str]) -> str:
    return random.choice(stickers)
