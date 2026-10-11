"""Entry point: keeps the bot polling for as long as the process lives.

Replit restarts a Reserved VM whose process exits, but a crash loop there
costs minutes each time. The supervisor below recovers in seconds instead,
without the process ever going away.
"""

import logging
import os
import time

from telebot.apihelper import ApiTelegramException

from background import keep_alive
from bot.handlers import bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s %(message)s")
log = logging.getLogger("bot")

MAX_BACKOFF = 60

# ================= SUPERVISOR =================

def main():
    # A Reserved VM "Background Worker" has no port to serve; a "Web Server"
    # deployment is health-checked and needs one. KEEP_ALIVE=0 skips the thread.
    if os.getenv("KEEP_ALIVE", "1") != "0":
        keep_alive()

    # Telegram refuses getUpdates while a webhook is registered, so one left
    # over from an earlier experiment would answer 409 on every poll.
    try:
        bot.remove_webhook()
    except Exception:
        log.warning("remove_webhook failed, continuing", exc_info=True)

    backoff = 1
    while True:
        try:
            log.info("polling")
            bot.infinity_polling(timeout=20, long_polling_timeout=20)
            # Returns only if something called bot.stop_polling().
            log.warning("polling returned, restarting")
            backoff = 1
        except ApiTelegramException as e:
            if e.error_code == 409:
                log.error("409 conflict: another instance is polling this "
                          "token. Stop the workspace copy or the old "
                          "deployment.")
            else:
                log.error("telegram api error %s", e.error_code, exc_info=True)
        except Exception:
            log.error("polling crashed", exc_info=True)

        time.sleep(backoff)
        backoff = min(backoff * 2, MAX_BACKOFF)


if __name__ == "__main__":
    main()
