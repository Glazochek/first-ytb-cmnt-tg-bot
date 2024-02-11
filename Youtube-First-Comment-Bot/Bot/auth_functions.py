from variables import *
from credentials_functions import *
from bs4 import BeautifulSoup
from oauth2client.client import FlowExchangeError
from access_functions import access

message_tutorial = """
👤 How to Authenticate?

We will use your google account to create comment in youtube

1. You need to choose your google account
2. Click 'additional settings' -> 'Go to the page'
3. Click 'Continue' and return to the telegram bot
4. Send copied code from webpage
"""

keyboard_reply_1 = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton("start searching")]],
    resize_keyboard=True,
    one_time_keyboard=True)

check_auth_btn = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Check authentification", callback_data="check_auth")]])

auth_second_time = True


def get_authenticated_service():
    return flow.step1_get_authorize_url()


def tutorial_auth(update: Update, context: CallbackContext):
    global auth_second_time
    telegram_user_id = update.effective_chat.id
    if access(telegram_user_id) and auth_second_time:
        if plan_info["name"] == "Basic":
            auth_second_time = False
        url = get_authenticated_service()
        if url:
            data_file = ROOT_DIR + "/Data/"
            context.bot.send_media_group(update.effective_chat.id, media=[
                InputMediaPhoto(open(f"{data_file}/imgs/1.jpg", "rb").read()),
                InputMediaPhoto(open(f"{data_file}/imgs/2.jpg", "rb").read()),
                InputMediaPhoto(open(f"{data_file}/imgs/3.jpg", "rb").read())])
            context.bot.send_message(update.effective_chat.id, message_tutorial, reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Google authentication", url=url, callback_data="url")]]))
        else:
            context.bot.send_message(update.effective_chat.id, text="You already authenticated")
    elif not auth_second_time:
        context.bot.send_message(update.effective_chat.id, text="You can't registrate more than once!")


def check_auth(update: Update, context: CallbackContext):
    telegram_user_id = update.effective_chat.id
    if access(telegram_user_id):
        code = update.message.text
        try:
            credentials = flow.step2_exchange(code)
            put_credentials(telegram_user_id, credentials)

            message = "Success authentication!\nNow let's try video checking function"
            reply_markup = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(f"Start search video")]],
                resize_keyboard=True,
                one_time_keyboard=True)
            bot.send_message(telegram_user_id, message, reply_markup=reply_markup)
            return ConversationHandler.END
        except FlowExchangeError:
            message = "Incorrect code, try again"
            bot.send_message(telegram_user_id, message)


def log_out(update: Update, context: CallbackContext):
    telegram_user_id = update.message.from_user.id
    if access(telegram_user_id) and plan_info["name"] in ["Medium", "Premium"]:
        file_path = CREDENTIALS_STORAGE+str(update.message.from_user.id)+".json"
        if os.path.exists(file_path):
            os.remove(file_path)
            bot.send_message(update.message.from_user.id, "You was logged out!")



