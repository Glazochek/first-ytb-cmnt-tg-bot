from variables import *
from tokens_functions import manage_tokens, manage_user_info, create_user_info
from access_functions import access
from auth_functions import tutorial_auth

main_buttons = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton("See my plan"), KeyboardButton("registration")]],
    resize_keyboard=True,
    one_time_keyboard=True)


def start(update: Update, context: CallbackContext):
    telegram_user_id = update.message.from_user.id
    if access(telegram_user_id):
        context.bot.send_message(chat_id=telegram_user_id, text=message_start,
                                 parse_mode="HTML", reply_markup=main_buttons)
        if str(telegram_user_id) in admin_tg_id:
            context.bot.send_message(chat_id=telegram_user_id, text=message_start_admin,
                                     parse_mode="HTML")
        return ConversationHandler.END


def plan(update: Update, context: CallbackContext):
    telegram_user_id = update.message.from_user.id
    if access(telegram_user_id):
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(f"Start search video")]],
            resize_keyboard=True,
            one_time_keyboard=True)
        context.bot.send_message(chat_id=telegram_user_id,
                                 text=message_plan, parse_mode="HTML",
                                 reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("registration")]],
        resize_keyboard=True,
        one_time_keyboard=True) if str(telegram_user_id) not in user_info.keys() else reply_markup)


def start_reg(update: Update, context: CallbackContext):
    telegram_user_id = update.message.from_user.id
    if access(telegram_user_id):
        if str(telegram_user_id) in user_info.keys():
            if "None" not in user_info[str(telegram_user_id)].values():
                if f"{telegram_user_id}.json" not in os.listdir(CREDENTIALS_STORAGE):
                    tutorial_auth(update, context)
                    return CHECK_AUTH
                else:
                    message = "You are already registered!"
                    bot.send_message(telegram_user_id, message)
                    return ConversationHandler.END
        create_user_info(telegram_user_id)
        context.bot.send_message(chat_id=update.message.chat_id, text="Write channel_id", reply_markup=ReplyKeyboardRemove())
        return CHECK_VIDEOS


# @app.route("/callback")
# def callback():
#     code = request.url.split("code=")[1].split("&")[0]
#     return code
#     # global bot
#     # telegram_user_id = cache.get("telegram_user_id")
#     # manage_tokens(telegram_user_id, 0)
#     # code = request.url.split("code=")[1].split("&")[0]
#     #
#     # credentials = flow.step2_exchange(code)
#     # put_credentials(telegram_user_id, credentials)
#     #
#     # message = "Success authentication!\nNow let's try video checking function"
#     # reply_markup = ReplyKeyboardMarkup(
#     # keyboard=[[KeyboardButton(f"Start search video ({user_tokens[telegram_user_id]})")]],
#     # resize_keyboard=True,
#     # one_time_keyboard=True)
#     # bot.send_message(telegram_user_id, message, reply_markup=reply_markup)
#
#     # return redirect("https://t.me/test_18273842589437_bot")


def open_db(update: Update, context: CallbackContext):
    global list_of_ids
    if str(update.message.from_user.id) in admin_tg_id:
        fields = ["user_id", "playlist_id", "comment", "tokens"]
        with open(DATA_FUNCTIONS + "users_data.csv", 'w') as f:
            write = csv.writer(f)
            write.writerow(fields)
            write.writerows([[f, *user_info[f].values()] for f in user_info.keys()])
        doc = open(DATA_FUNCTIONS + "users_data.csv", "rb").read()
        context.bot.send_document(chat_id=update.message.chat_id, document=doc, filename="users_data.csv")


def send_msg_user(update: Update, context: CallbackContext):
    if str(update.message.from_user.id) in admin_tg_id:
        _, user_id, message = update.message.text.split()
        context.bot.send_message(user_id, message)
        context.bot.send_message(update.message.from_user.id, "Completed!")


def send_msg_users(update: Update, context: CallbackContext):
    if str(update.message.from_user.id) in admin_tg_id:
        _, message = update.message.text.split()
        users = user_info.keys()
        for user in users:
            context.bot.send_message(user, message)
        context.bot.send_message(update.message.from_user.id, "Completed!")


def invalid_command(update: Update, context: CallbackContext):
    telegram_user_id = update.message.from_user.id
    if access(telegram_user_id):
        update.message.reply_text(
            f"Invalid command '{update.message.text}'", reply_markup=ReplyKeyboardRemove()
        )



