import telebot
from . import services
from .config import (
    TOKEN,
    START_STICKER,
    WEBSITE_STICKER,
    TELEBOT_STICKER,
    TURTLE_STICKER,
    FALLBACK_STICKERS,
    build_main_keyboard,
    build_telebot_keyboard,)

bot = telebot.TeleBot(TOKEN)

# ================= START =================

@bot.message_handler(commands=['Begin', 'begin', 'start', 'Start'])
def start_message(message):
    bot.send_sticker(message.chat.id, START_STICKER)
    bot.send_message(
        message.chat.id,
        "Hello! 😉\nUse the /info command to open the menu 🧾.")

# ================= MENU =================

@bot.message_handler(commands=['info'])
def button_message(message):
    bot.send_message(
        message.chat.id,
        "Please choose what you need:\n"
        "1. website - link to the official website\n"
        "2. telebot - guide on creating a Telegram bot in Python\n"
        "3. tkinter — basic tkinter tutorial\n"
        "4. turtle — how the turtle library works\n"
        "5. pillow — how the Pillow library works\n"
        "6. wiki — definition from Wikipedia (first 1000 chars)\n"
        "7. picture — send a random picture\n"
        "8. time — current New-York time\n"
        "9. date — current date (day/month/year)",
        reply_markup=build_main_keyboard())

# ================= MAIN HANDLER =================

@bot.message_handler(content_types=['text'])
def message_reply(message):
    text = message.text

    # ---------- WEBSITE ----------
    if text == "website":
        bot.send_sticker(message.chat.id, WEBSITE_STICKER)
        bot.send_message(
            message.chat.id,
            "http://all.about.python.ru.tilda.ws/",
            disable_web_page_preview=True)

    # ---------- WIKIPEDIA SEARCH ----------
    elif '#' in text:
        result = services.search_wikipedia(text[1:])
        if result:
            bot.send_message(message.chat.id, result)
        else:
            bot.send_message(
                message.chat.id,
                "Unfortunately, Wikipedia has no information about this.")
            bot.send_sticker(
                message.chat.id,
                "CAACAgIAAxkBAAEHy7hj8MvAcf6NjZQ7sPFiyE6ZPA82FQACHxQAAtgpqEs-rjW3bsz-Ji4E")

    # ---------- WIKI HELP ----------
    elif text == "wiki":
        bot.send_message(
            message.chat.id,
            "Send me # followed by any word, and I will find its meaning in Wikipedia.")
        bot.send_photo(message.chat.id, services.get_wiki_image())

    # ---------- TELEBOT MENU ----------
    elif text == "telebot":
        bot.send_sticker(message.chat.id, TELEBOT_STICKER)
        bot.send_message(
            message.chat.id,
            "Choose a chapter:"
            "\n 1. sticker - how to send a sticker using telebot;"
            "\n 2. library - where and how to install all the necessary libraries 📔;"
            "\n 3. greetings - how to create the bot's draft and say 'Hi ✌';"
            "\n 4. button - how to create a button for the bot ⏸;"
            "\n 5. source - articles' sources 📜;"
            "\n 6. back - go back to menu 🧾.",
            reply_markup=build_telebot_keyboard())

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
    elif text == "back":
        bot.send_message(
            message.chat.id,
            "You returned to the main menu. Use /info if you forgot the commands.",
            reply_markup=build_main_keyboard())

    # ---------- STICKER ----------
    elif text == "sticker":
        bot.send_message(
            message.chat.id,
            "Use:\n"
            "bot.send_sticker(message.chat.id, sticker_id)\n\n"
            "To find sticker ID, use @idstickerbot.")

    # ---------- SOURCE ----------
    elif text == "source":
        bot.send_message(
            message.chat.id,
            "https://habr.com/ru/post/580408/\nThanks for reading!")

    # ---------- PILLOW ----------
    elif text == "pillow":
        bot.send_message(
            message.chat.id,
            "ENG: https://realpython.com/image-processing-with-the-python-pillow-library/"
            "\nRU: https://pythonru.com/biblioteki/osnovnye-vozmozhnosti-biblioteki-python-imaging-library-pillow-pil"
            "\nThanks for reading!")

    # ---------- TURTLE ----------
    elif text == "turtle":
        bot.send_sticker(message.chat.id, TURTLE_STICKER)
        bot.send_message(
            message.chat.id,
            "ENG: https://dl.acm.org/doi/10.1145/3732789"
            "\nRU: https://gvard.github.io/py/turtle/"
            "\nThanks for reading!")

    elif text == "picture":
        bot.send_photo(message.chat.id, services.get_random_image())

    elif text == "time":
        bot.send_message(message.chat.id, f"🕖 {services.get_ny_time()}")

    elif text == "date":
        bot.send_message(message.chat.id, f"🗓 {services.get_current_date()}")

    else:
        sticker = services.random_fallback_sticker(FALLBACK_STICKERS)
        bot.send_sticker(message.chat.id, sticker)
        bot.send_message(
            message.chat.id,
            "Hmm… I don't understand 🤔\nPlease rephrase your request."
        )