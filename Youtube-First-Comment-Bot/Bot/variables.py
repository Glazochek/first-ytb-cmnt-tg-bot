import telegram
import os
import pathlib
import requests
import csv
import json

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

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

CREDENTIALS_STORAGE = f"{ROOT_DIR}/Data/credentials/"
CLIENT_SECRETS_FILE = f"{ROOT_DIR}/Data/oauth_data/client_secret.json"
DATA_FUNCTIONS = f"{ROOT_DIR}/Data/data_functions/"
youtube_ssl_url = f"{ROOT_DIR}/Data/oauth_data/youtube-v3-discoverydocument.json"
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

USER_INFO = f"{ROOT_DIR}/Data/data_functions/user_info.json"

with open(ROOT_DIR+"/bot_config.json", "r") as conf:
    bot_config = json.load(conf)
    plan_info = bot_config["plan"]
    admin_tg_id = bot_config["admin_chat_id"]
    token = bot_config["token"]
    client_id = bot_config["client_id"]
    client_secret = bot_config["client_secret"]
    message_plan = plan_info["text_plan"]

# intervel = 5
# time_of_search = 30

ytb = None
# telegram_user_id = None

# app = Flask(__name__)
# app.secret_key = "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"
# os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
# cache.init_app(app=app, config={"CACHE_TYPE": "filesystem",'CACHE_DIR': Path('/tmp')})

bot = telegram.Bot(token)

CHECK_VIDEOS, COMMENT_YOUTUBE, CHECK_AUTH = range(3)

try:
    with open(USER_INFO, "r") as file:
        user_info = json.load(file)
except:
    user_info = {}

list_of_ids = list(user_info.keys())+[admin_tg_id]


host = "https://upcmts.com/callback"

flow = OAuth2WebServerFlow(
    client_id=client_id,
    client_secret=client_secret,
    scope=[YOUTUBE_READ_WRITE_SSL_SCOPE],
    redirect_uri=host,
    access_type='offline',
    prompt='consent'
)

message_start = ("<b>Welcome!</b>"
"\nThis bot notifies you about new uploads on YouTube channels or playlists."
"\n\nChecking for new videos:"
"\n<i>/check_videos</i>"
f"\n\nSetting of searching:"
f" \n<i>/change_comment text</i>"
f" \n{'<i>/change_channel channel_id</i>' if plan_info['name'] in ['Medium', 'Premium'] else ''}"
f" \n{'<i>/log_out</i>' if plan_info['name'] in ['Medium', 'Premium'] else ''}"
"\n\nTokens:"
" \n<i>/my_tokens</i>")

no_access_txt = "You have no access!"

message_start_admin = """
Admin commands:
 <i>/access_to chat_id</i>
 <i>/see_users</i>
 <i>/add_tokens user_id num_of_token</i>
 <i>/change_user_channel user_id channel_id</i>
 <i>/send_msg_user user_id message</i>
 <i>/send_msg_users message</i>
 <i>/set_time_search seconds</i>
"""


#
# {"token": "6925547076:AAE9zI9VzaSTzVtMjDlIBHYCj6iR950unE8",
#   "client_id": "572838302078-70orpvgrnv0jf38pukbi8f1ue2cqbaos.apps.googleusercontent.com",
#   "client_secret": "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",
#   "admin_chat_id": "747278740",
#   "plan": {
#     "name": "Basic",
#     "text_plan": "Your plan: BASIC 🪨 \n\n✖️ Choose youtube channels \n✖️Several accounts and logout \n✅️ change a comment text \n✅️ Use video checking function 5 times"
#   }
# }
#
# {"token": "6925547076:AAE9zI9VzaSTzVtMjDlIBHYCj6iR950unE8",
#   "client_id": "572838302078-70orpvgrnv0jf38pukbi8f1ue2cqbaos.apps.googleusercontent.com",
#   "client_secret": "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",
#   "admin_chat_id": "1977988206",
#   "plan": {
#     "name": "Premium",
#     "text_plan": "Your plan: PREMIUM ⭐️\n\n✅️ Choose youtube channels\n✅️️ Several accounts and logout\n✅️️ change a comment\n✅️ Use video checking function 1000 times"
#   }
# }