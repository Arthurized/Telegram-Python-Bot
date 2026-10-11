"""
Tiny web server for host types that health-check an open port, such as
Replit's "Web Server" deployment. A Background Worker, a VPS or a local
machine does not need it: set KEEP_ALIVE=0 there.
"""

import os
from threading import Thread

from flask import Flask


app = Flask('')

@app.route('/')
def home():
  return "I'm alive!!!!!"

def run():
  # Imported here so the module still loads where waitress is absent and
  # KEEP_ALIVE=0 means this never runs.
  from waitress import serve
  serve(app, host='0.0.0.0', port=int(os.getenv("PORT", "8080")))

def keep_alive():
  # Daemon, so a dead main thread cannot leave the process lingering while
  # it still holds the Telegram token.
  Thread(target=run, daemon=True).start()
