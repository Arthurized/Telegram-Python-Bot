import os
from dotenv import load_dotenv
from telebot import types
load_dotenv()

# ================= TOKEN && PATHS =============

TOKEN = os.getenv("TELEGRAM_TOKEN")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "images")

# ================= STICKERS =================

START_STICKER = "CAACAgEAAxkBAAEHlddj3nBaiVqvH4a-Cz8EcNSjTGjbNgACVTMAAtpxZgdUSKRTBteYgS4E"
WEBSITE_STICKER = "CAACAgIAAxkBAAEHldtj3nEffjcLFcwdqE7sxv382mbzmwACZwADHwFMFQMvnzs0dPL6LgQ"
TELEBOT_STICKER = "CAACAgIAAxkBAAEHld1j3nEuF3ac8bylAyAAAUPjU2dh1pUAAnoAAx8BTBUGkOkq8OOpGS4E"
TURTLE_STICKER = "CAACAgIAAxkBAAEHlbtj3mSQIJ7DX4cRRL-E16TSm8wyEwACGQADkP2aFeu-zHekaJbILgQ"

FALLBACK_STICKERS = [
    "CAACAgIAAxkBAAEHmUlj38-RpzudywOJuvF1ZAGHf_gHEAACQxAAAr8VUEhdiv9zhwK4Sy4E",
    "CAACAgIAAxkBAAEHmUtj38-cTaRfiMzCTaluXA7Rik0ePQACyhAAAmpmWUj9olDnZhiLrS4E",
    "CAACAgIAAxkBAAEHmU1j38-iaw8E5KSJSAR1eDvXzDB7qwAC4w8AApusUEglwx9133Xr6C4E",
    "CAACAgIAAxkBAAEHmU9j38-1LQ3c2LPf53pPFhs65jCPtAACdwADHwFMFWrJq8ZPn5NrLgQ",
    "CAACAgIAAxkBAAEHmVdj39Ds6kiJqc5tLnu37Q0lYz5zuwACcwADHwFMFV5TSS8DCffbLgQ",
    "CAACAgIAAxkBAAEHmVFj38_HefgFMEBkokfxsaFzapp73AACaQADHwFMFSgkY_ekuc6xLgQ",]

# ================= KEYBOARD =================

def build_main_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["website", "telebot", "tkinter", "turtle",
        "pillow", "wiki", "picture", "time", "date"]
    for b in buttons:
        markup.add(types.KeyboardButton(b))
    return markup


def build_telebot_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["sticker", "library", "greetings", "button", "source", "back"]
    for b in buttons:
        markup.add(types.KeyboardButton(b))
    return markup

