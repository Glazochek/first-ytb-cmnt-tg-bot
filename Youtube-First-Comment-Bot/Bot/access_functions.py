import os

from variables import *


def save(var, file):
    with open(file, "w") as f:
        json.dump(var, f)

def access(user_id):
    if str(user_id) in user_info.keys():
        return True
    return False


def access_to(update: Update, context: CallbackContext):
    data = update.message.text.split()
    if str(update.message.from_user.id) in admin_tg_id and len(data) == 2:
        user_id = data[1]
        if plan_info["name"] in ["Premium"]:
            user_info[str(user_id)] = {"playlist_id": "None", "comment": "None", "tokens": 1000}
        else:
            user_info[str(user_id)] = {"playlist_id": "None", "comment": "None", "tokens": 5}
        save(user_info, USER_INFO)
        bot.send_message(update.message.from_user.id, f"Access added to user_id {data[1]}")
    else:
        bot.send_message(update.message.from_user.id, no_access_txt)

def delete_access(user_id):
    del user_info[str(user_id)]

def delete_credentials(user_id):
    os.remove(CREDENTIALS_STORAGE+f"/{user_id}.json")


def delete_user(update: Update, context: CallbackContext):
    data = update.message.text.split()
    if str(update.message.from_user.id) in admin_tg_id and len(data) == 2:
        user_id = data[1]
        delete_access(user_id)
        delete_credentials(user_id)
        save(user_info, USER_INFO)
        bot.send_message(update.message.from_user.id, f"User {user_id} was deleted!")
        bot.send_message(user_id, f"Your access was deleted!")
    else:
        bot.send_message(update.message.from_user.id, no_access_txt)