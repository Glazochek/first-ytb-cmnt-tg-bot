from .variables import *
from .auth_functions import *
from .credentials_functions import put_credentials
from .tokens_functions import manage_tokens
from .access_functions import access


main_buttons = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton("See my plan"), KeyboardButton("registration")]],
    resize_keyboard=True,
    one_time_keyboard=True)


def start(update: Update, context: CallbackContext):
    global telegram_user_id
    if access(update.message.from_user.id):
        telegram_user_id = update.message.from_user.id
        cache.set("telegram_user_id", update.message.from_user.id)
        context.bot.send_message(chat_id=update.message.chat_id, text=message_start,
                                 parse_mode="HTML", reply_markup=main_buttons)


def plan(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=message_plan, parse_mode="HTML",
                             reply_markup=ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton("registration")]],
    resize_keyboard=True,
    one_time_keyboard=True))


def start_reg(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.message.chat_id, text="Write channel_id", reply_markup=ReplyKeyboardRemove())
    return CHECK_VIDEOS


@app.route("/callback")
def callback():
    telegram_user_id = cache.get("telegram_user_id")
    manage_tokens(telegram_user_id, 0)
    code = request.url.split("code=")[1].split("&")[0]

    credentials = flow.step2_exchange(code)
    put_credentials(telegram_user_id, credentials)

    message = "Success authentication!\nNow let's try video checking function"
    reply_markup = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(f"Start search video ({user_tokens[telegram_user_id]})")]],
    resize_keyboard=True,
    one_time_keyboard=True)
    bot.send_message(telegram_user_id, message, reply_markup=reply_markup)
    return redirect("https://t.me/test_18273842589437_bot")



def open_db(update: Update, context: CallbackContext):
    global list_of_ids
    if str(update.message.from_user.id) in admin_tg_id:
        fields = ["user_id", "tokens"]
        with open('Youtube-First-Comment-Bot/Data/data_functions/users_data.csv', 'w') as f:
            write = csv.writer(f)
            write.writerow(fields)
            write.writerows([[f, user_tokens[f]] for f in user_tokens.keys()])
        doc = open("Youtube-First-Comment-Bot/Data/data_functions/users_data.csv", "rb").read()
        context.bot.send_document(chat_id=update.message.chat_id, document=doc, filename="users_data.csv")


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Move was canceled", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END



