from variables import *

def access(user_id):
    if str(user_id) in list_of_ids:
        return True
    return False


def access_to(update: Update, context: CallbackContext):
    data = update.message.text.split()
    if str(update.message.from_user.id) in admin_tg_id and len(data) == 2:
        user_id = data[1]
        list_of_ids.append(user_id)
        if plan_info["name"] in ["Premium"]:
            user_info[str(user_id)] = {"playlist_id": "None", "comment": "None", "tokens": 1000}
        else:
            user_info[str(user_id)] = {"playlist_id": "None", "comment": "None", "tokens": 5}
        bot.send_message(update.message.from_user.id, f"Access added to user_id {data[1]}")
    else:
        bot.send_message(update.message.from_user.id, no_access_txt)