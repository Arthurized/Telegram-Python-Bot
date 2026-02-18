from background import keep_alive
from bot.handlers import bot

if __name__ == "__main__":
    keep_alive()
    bot.polling(non_stop=True, interval=1)
