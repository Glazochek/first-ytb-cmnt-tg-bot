from .variables import *

def access(user_id):
    if str(user_id) in list_of_ids:
        return True
    return True


def open_access(update: Update, context: CallbackContext):
    if str(update.message.from_user.id) in admin_tg_id:
        list_of_ids.append(str(update.message.from_user.id))
        with open(ACCESS_IDS, "w") as file:
            file.write("\n".join(set(list_of_ids)))
        context.bot.send_message(chat_id=update.message.chat_id, text="Access is open 🔓\n use /start again")
