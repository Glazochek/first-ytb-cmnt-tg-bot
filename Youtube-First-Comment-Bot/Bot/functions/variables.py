import telegram
import os
import pathlib
import requests
import csv
import json

from flask import Flask, session, abort, redirect, request
from webhook.common import cache
from pathlib import Path
from waitress import serve
from multiprocessing import Process

# from apiclient.discovery import build_from_document
from builtins import FileNotFoundError
from pip._vendor import cachecontrol

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build_from_document
from oauth2client import file, client, tools
from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError
from oauth2client.file import Storage

from telegram import Update, Bot
from telegram.ext import (Updater, filters, CommandHandler, MessageHandler, ConversationHandler,
                          CallbackQueryHandler, CallbackContext, JobQueue)
from telegram import (KeyboardButton, InlineKeyboardButton, ReplyKeyboardRemove,
                      InputMediaPhoto, ReplyKeyboardMarkup, InlineKeyboardMarkup)


CREDENTIALS_STORAGE = "Youtube-First-Comment-Bot/Data/credentials/"
CLIENT_SECRETS_FILE = "/oauth_data/client_secret.json"
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0
To make this sample run you will need to populate the client_secrets.json file
found at:
   %s
with information from the APIs Console
https://console.developers.google.com
For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE))

TOKENS_FILE = "Youtube-First-Comment-Bot/Data/user_tokens.json"
ACCESS_IDS = "Youtube-First-Comment-Bot/Data/access_ids.txt"

admin_tg_id = "1977988206"

intervel = 5
time_of_search = 30

comment = "good"
playlist_id = None
ytb = None
telegram_user_id = None

app = Flask(__name__)
app.secret_key = "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"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

cache.init_app(app=app, config={"CACHE_TYPE": "filesystem",'CACHE_DIR': Path('/tmp')})


token = '6925547076:AAE9zI9VzaSTzVtMjDlIBHYCj6iR950unE8'
bot = telegram.Bot(token)

CHECK_VIDEOS, COMMENT_YOUTUBE = range(2)

try:
    with open(ACCESS_IDS, "r") as file:
        list_of_ids = [i.replace("\n", "") for i in file.readlines()]
except FileNotFoundError:
    list_of_ids = [admin_tg_id]

try:
    with open(TOKENS_FILE, "r") as file:
        user_tokens = json.load(file)
except FileNotFoundError:
    user_tokens = {}

host = "127.0.0.1:5000"
flow = OAuth2WebServerFlow(
    client_id="572838302078-7jfh771jo46m65804bq9jo9fh1j1818i.apps.googleusercontent.com",
    client_secret="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",
    scope=[YOUTUBE_READ_WRITE_SSL_SCOPE],
    redirect_uri=f"http://{host}/callback",
    access_type='offline',
    prompt='consent'
)

plans = [
"""
Your plan: BASIC 🪨

 ✖️ Choose youtube channels
 ✖️ write a comment
 ✖️ Use video checking function
 ✖️ Search several times
""",
"""
Your plan: MEDIUM 🧩

 ✅️ Choose youtube channels
 ✅️️ write a comment
 ✅️ Use video checking function 5 times
""",
"""
Your plan: PREMIUM ⭐️

 ✅️ Choose youtube channels
 ✅️ write a comment
 ✅️ Use video checking function ♾️times
"""
]

message_plan = plans[1]

message_start = """
<b>Welcome!</b>
This bot notifies you about new uploads on YouTube channels or playlists.

Checking for new videos:
 <i>/checkvideos channel_id</i>

Setting of searching:
 <i>/change_comment text</i>
 <i>/set_time_of_search seconds</i>

Tokens:
 <i>/my_tokens</i>

Admin commands:
 <i>/open_access</i>
 <i>/add_tokens user_id num_of_token</i>
"""
