from variables import *
from access_functions import access


def save(var, file):
    with open(file, "w") as f:
        json.dump(var, f)


def manage_tokens(user_id, change=None):
    if str(user_id) in user_info.keys():
        if "tokens" in user_info[str(user_id)].keys():
            user_info[str(user_id)]["tokens"] += change
            if user_info[str(user_id)]["tokens"] < 0:
                user_info[str(user_id)]["tokens"] = 0
            save(user_info, USER_INFO)
            return user_info[str(user_id)]["tokens"]


def my_tokens(update: Update, context: CallbackContext):
    if access(update.message.from_user.id):
        if f"{update.message.from_user.id}.json" in os.listdir(CREDENTIALS_STORAGE):
            manage_user_info(str(update.message.from_user.id))
            current_tokens = user_info[str(update.message.from_user.id)]["tokens"]
            message = f"You have {current_tokens} {'token' if current_tokens < 2 else 'tokens'}"
            context.bot.send_message(chat_id=update.message.chat_id, text=message)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text="You should log in!")


def add_tokens(update: Update, context: CallbackContext):
    if str(update.message.from_user.id) in admin_tg_id:
        if len(update.message.text.split()) == 3:
            user_id, num_of_tokens = update.message.text.split()[1], int(update.message.text.split()[2])
            manage_tokens(user_id, num_of_tokens)
            context.bot.send_message(chat_id=update.message.chat_id, text=f"You added to {user_id} {num_of_tokens} tokens")
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text=f"You must use this constraction:\n "
                                                                          f"/add_tokens user_id num_of_token")


def create_user_info(user_id):
    if plan_info["name"] in ["Premium"]:
        user_info[str(user_id)] = {"playlist_id": "None", "comment": "None", "tokens": 1000}
    else:
        user_info[str(user_id)] = {"playlist_id": "None", "comment": "None", "tokens": 5}
    save(user_info, USER_INFO)


def manage_user_info(user_id, channel_id=None, comnt=None):
    if channel_id:
        user_info[str(user_id)]["playlist_id"] = channel_id
    if comnt:
        user_info[str(user_id)]["comment"] = comnt
    save(user_info, USER_INFO)

