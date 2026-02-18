"""
Extra folder with all bots code in one file
(except for env, for security reasons). Beginner-friendly.

If you are using extra.py, please download all the images into
the same folder.
"""

import os
from dotenv import load_dotenv # getting a token securely
load_dotenv()
import pytz
from background import keep_alive
import telebot
import wikipedia
import random
from datetime import datetime, date
from telebot import types
from PIL import Image

# ================= KEYBOARD =================

markup_1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("website")
item2 = types.KeyboardButton("telebot")
item3 = types.KeyboardButton("tkinter")
item4 = types.KeyboardButton("turtle")
item5 = types.KeyboardButton("pillow")
item6 = types.KeyboardButton("wiki")
item7 = types.KeyboardButton("picture")
item8 = types.KeyboardButton("time")
item9 = types.KeyboardButton("date")
markup_1.add(item1, item2, item3, item4, item5, item6, item7, item8, item9)

# ================= TOKEN =================

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ================= START =================

@bot.message_handler(commands=['Begin', 'begin', 'start', 'Start'])
def start_message(message):
    bot.send_sticker(message.chat.id,
                     "CAACAgEAAxkBAAEHlddj3nBaiVqvH4a-Cz8EcNSjTGjbNgACVTMAAtpxZgdUSKRTBteYgS4E")
    bot.send_message(
        message.chat.id,
        "Hello! 😉\nUse the /info command to open the menu 🧾.")

# ================= MAIN MENU =================

@bot.message_handler(commands=['info'])
def button_message(message):
    bot.send_message(
        message.chat.id,
        "Please choose what you need:\n"
        "1. website — link to the official website\n"
        "2. telebot — guide on creating a Telegram bot in Python\n"
        "3. tkinter — basic tkinter tutorial\n"
        "4. turtle - how the turtle library works\n"
        "5. pillow — how the Pillow library works\n"
        "6. wiki — definition from Wikipedia (first 1000 chars)\n"
        "7. picture — send a random picture\n"
        "8. time — current New-York time\n"
        "9. date — current date (day/month/year)",
        reply_markup=markup_1)

# ================= MAIN HANDLER =================

@bot.message_handler(content_types = ['text'])
def message_reply(message):

    # ---------- WEBSITE ----------
    if message.text == "website":
        bot.send_sticker(message.chat.id,
                         "CAACAgIAAxkBAAEHldtj3nEffjcLFcwdqE7sxv382mbzmwACZwADHwFMFQMvnzs0dPL6LgQ")
        bot.send_message(
            message.chat.id,
            "http://all.about.python.ru.tilda.ws/",
            disable_web_page_preview=True)

    # ---------- WIKIPEDIA SEARCH ----------
    elif '#' in message.text:
        try:
            wikipedia.set_lang("en")
            ny = wikipedia.page(message.text[1:], auto_suggest=False)
            wikitext = ny.content[:1000]

            sentences = wikitext.split('.')
            sentences = sentences[:-1]

            clean_text = ''
            for x in sentences:
                if '==' not in x and len(x.strip()) > 3:
                    clean_text += x + '.'
                else:
                    break

            bot.send_message(message.chat.id, clean_text)

        except Exception:
            bot.send_message(
                message.chat.id,
                "Unfortunately, Wikipedia has no information about this.")
            bot.send_sticker(
                message.chat.id,
                "CAACAgIAAxkBAAEHy7hj8MvAcf6NjZQ7sPFiyE6ZPA82FQACHxQAAtgpqEs-rjW3bsz-Ji4E")

    # ---------- WIKI HELP ----------
    elif message.text == "wiki":
        bot.send_message(
            message.chat.id,
            "Send me # followed by any word, and I will find its meaning in Wikipedia.")
        br = Image.open("wiki.jpg")
        bot.send_photo(message.chat.id, br)

    # ---------- TELEBOT MENU ----------
    elif message.text == "telebot":
        bot.send_sticker(message.chat.id,
                         "CAACAgIAAxkBAAEHld1j3nEuF3ac8bylAyAAAUPjU2dh1pUAAnoAAx8BTBUGkOkq8OOpGS4E")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("sticker"),
                   types.KeyboardButton("library"), types.KeyboardButton("greetings"),
                   types.KeyboardButton("button"), types.KeyboardButton("source"),
                   types.KeyboardButton('back')
        )

        bot.send_message(message.chat.id,
        "Choose a chapter:"
            "\n 1. sticker - how to send a sticker using telebot;"
            "\n 2. library - where and how to install all the necessary libraries 📔;"
            "\n 3. greetings - how to create the bot's draft and say 'Hi ✌';"
            "\n 4. button - how to create a button for the bot ⏸;"
            "\n 5. source - articles' sources 📜;"
            "\n 6. back - go back to menu 🧾.", reply_markup=markup)

    # ---------- GREETINGS ----------
    elif message.text == 'greetings':
        bot.send_message(
            message.chat.id,
            "First, get a token from @BotFather.\n\n"
            "Example bot greeting:\n"
            "import telebot\n"
            "token = 'YOUR_TOKEN'\n"
            "bot = telebot.TeleBot(token)\n\n"
            "@bot.message_handler(commands=['start'])\n"
            "def start_message(message):\n"
            "    bot.send_message(message.chat.id, 'Hello ✌')\n\n"
            "bot.infinity_polling()")

    # ---------- BUTTON GUIDE ----------
    elif message.text == 'button':
        bot.send_message(
            message.chat.id,
            "How to create buttons:\n"
            "1) Create markup:\n"
            "   markup = types.ReplyKeyboardMarkup(resize_keyboard=True)\n"
            "2) Create buttons:\n"
            "   btn = types.KeyboardButton('text')\n"
            "3) Add buttons:\n"
            "   markup.add(btn)\n"
            "4) Attach to message using reply_markup=markup")

    # ---------- TKINTER ----------
    elif message.text == 'tkinter':
        bot.send_message(
            message.chat.id,
            "3-hour tkinter course:\n"
            "https://www.youtube.com/watch?v=YXPyB4XeYLA")

    # ---------- LIBRARY ----------
    elif message.text == 'library':
        bot.send_message(
            message.chat.id,
            "To install pyTelegramBotAPI:\n"
            "Windows: pip install pyTelegramBotAPI\n"
            "macOS/Linux: pip3 install pyTelegramBotAPI\n\n"
            "Useful libraries: random, Pillow, datetime.")

    # ---------- BACK ----------
    elif message.text == "back":
        bot.send_message(
            message.chat.id,
            "You returned to the main menu. Use /info if you forgot the commands.",
            reply_markup=markup_1)

    # ---------- STICKER ----------
    elif message.text == "sticker":
        bot.send_message(
            message.chat.id,
            "Use:\n"
            "bot.send_sticker(message.chat.id, sticker_id)\n\n"
            "To find sticker ID, use @idstickerbot.")

    # ---------- SOURCE ----------
    elif message.text == "source":
        bot.send_message(
            message.chat.id,
            "https://habr.com/ru/post/580408/\nThanks for reading!")

    # ---------- PILLOW ----------
    elif message.text == "pillow":
        bot.send_message(
            message.chat.id,
            "ENG: https://realpython.com/image-processing-with-the-python-pillow-library/"
            "\nRU: https://pythonru.com/biblioteki/osnovnye-vozmozhnosti-biblioteki-python-imaging-library-pillow-pil"
            "\nThanks for reading!")

    # ---------- TURTLE ----------
    elif message.text == "turtle":
        bot.send_sticker(
            message.chat.id,
            "CAACAgIAAxkBAAEHlbtj3mSQIJ7DX4cRRL-E16TSm8wyEwACGQADkP2aFeu-zHekaJbILgQ")
        bot.send_message(
            message.chat.id,
            "ENG: https://dl.acm.org/doi/10.1145/3732789"
            "\nRU: https://gvard.github.io/py/turtle/"
            "\nThanks for reading!")

    # ---------- PICTURE ----------
    elif message.text == "picture":
        images = [Image.open("116.jpg"), Image.open("117.jpg"), Image.open("118.jpg"),
            Image.open("119.webp"), Image.open("120.jpg"), Image.open("121.webp"),
            Image.open("122.jpg"), Image.open("123.png"), Image.open("124.png"),
            Image.open("125.webp"), Image.open("126.webp"), Image.open("127.png"),
            Image.open("128.jpg"), Image.open("129.jpg"), Image.open("130.jpg"),
            Image.open("131.jpg"), Image.open("132.png"), Image.open("133.png"),
            Image.open("134.png"), Image.open("135.png"),
        ]
        bot.send_photo(message.chat.id, random.choice(images))

    # ---------- TIME ----------
    elif message.text == "time":
        ny_time = datetime.now(pytz.timezone("America/New_York"))
        bot.send_message(message.chat.id, f"🕖 {ny_time.strftime('%H:%M:%S')}")

    # ---------- DATE ----------
    elif message.text == "date":
        cd = date.today()
        bot.send_message(message.chat.id, f"🗓 {cd.strftime('%d-%m-%Y')}")

    # ---------- FALLBACK ----------
    else:
        wds = ["CAACAgIAAxkBAAEHmUlj38-RpzudywOJuvF1ZAGHf_gHEAACQxAAAr8VUEhdiv9zhwK4Sy4E",
               "CAACAgIAAxkBAAEHmUtj38-cTaRfiMzCTaluXA7Rik0ePQACyhAAAmpmWUj9olDnZhiLrS4E",
               "CAACAgIAAxkBAAEHmU1j38-iaw8E5KSJSAR1eDvXzDB7qwAC4w8AApusUEglwx9133Xr6C4E",
               "CAACAgIAAxkBAAEHmU9j38-1LQ3c2LPf53pPFhs65jCPtAACdwADHwFMFWrJq8ZPn5NrLgQ",
               "CAACAgIAAxkBAAEHmVdj39Ds6kiJqc5tLnu37Q0lYz5zuwACcwADHwFMFV5TSS8DCffbLgQ",
               "CAACAgIAAxkBAAEHmVFj38_HefgFMEBkokfxsaFzapp73AACaQADHwFMFSgkY_ekuc6xLgQ"]
        choice_1 = random.choice(wds)
        bot.send_sticker(message.chat.id, choice_1)
        bot.send_message(
            message.chat.id,
            "Hmm… I don't understand 🤔\nPlease rephrase your request.")

# ================= RUN =================

keep_alive()
bot.polling(non_stop=True, interval=1)
