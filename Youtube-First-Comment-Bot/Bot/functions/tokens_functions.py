from .variables import *
from .access_functions import access


def save_tokens():
    with open(TOKENS_FILE, "w") as file:
        json.dump(user_tokens, file)


def manage_tokens(user_id, change):
    current_tokens = user_tokens.get(user_id, 5)  # Set default tokens as 5 if user not found
    new_tokens = max(0, current_tokens + change)
    user_tokens[user_id] = new_tokens
    save_tokens()
    return new_tokens


def add_tokens(update: Update, context: CallbackContext):
    if str(update.message.from_user.id) in admin_tg_id:
        if len(update.message.text.split()) == 3:
            user_id, num_of_tokens = update.message.text.split()[1], int(update.message.text.split()[2])
            manage_tokens(user_id, num_of_tokens)
            context.bot.send_message(chat_id=update.message.chat_id, text=f"You added to {user_id} {num_of_tokens} tokens")
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text=f"You must use this constraction:\n "
                                                                          f"/add_tokens user_id num_of_token")


def my_tokens(update: Update, context: CallbackContext):
    if access(update.message.from_user.id):
        print(telegram_user_id, playlist_id)
        current_tokens = user_tokens.get(update.message.from_user.id, 5)

        message = f"You have {current_tokens} {'token' if current_tokens < 2 else 'tokens'}"

        context.bot.send_message(chat_id=update.message.chat_id, text=message)