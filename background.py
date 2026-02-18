"""
Tiny web server to keep the bot alive on free hosting platforms like Replit.
Not needed if running the bot on a VPS or local machine.
"""

from flask import Flask
from flask import request
from threading import Thread
import time
import requests


app = Flask('')

@app.route('/')
def home():
  return "I'm alive!!!!!"

def run():
  from waitress import serve
  serve(app, host='0.0.0.0', port=8080)

def keep_alive():
  t = Thread(target=run)
  t.start()