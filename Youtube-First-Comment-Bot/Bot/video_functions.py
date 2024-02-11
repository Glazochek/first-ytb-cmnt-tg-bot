import random
import time

import google

from variables import *
from another_functions import access
from tokens_functions import manage_tokens, manage_user_info
from auth_functions import tutorial_auth
from credentials_functions import refresh_token, get_credentials

cycle_number = 5
stop = False


def insert_comment(youtube, parent_id, text):
    insert_result = youtube.commentThreads().insert(
        part="snippet",
        body={
            "snippet": {
                "videoId": parent_id,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": text
                    }
                }
            }
        }
    )
    response = insert_result.execute()
    print("comment added", response)


def get_last_video_id(playlist_id):
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/playlist?list={playlist_id}&format=json"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        video_id = response.json().get("thumbnail_url", "").split("/")[4]
        return {"video_id": video_id} if video_id else None
    except requests.exceptions.RequestException as e:
        print(f"Unable to get playlist information: {e}")
        return None


def check_videos_async(context: CallbackContext):
    global ytb
    chat_id = context.job.context["chat_id"]
    comment = user_info[str(chat_id)]["comment"]
    playlist_id = user_info[str(chat_id)]["playlist_id"]

    storage = Storage(CREDENTIALS_STORAGE+str(chat_id)+".json")
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        access_token = refresh_token(
            "572838302078-cac36u8p8sg7vgo5q4d5vj38kvfer8q3.apps.googleusercontent.com",
            "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", credentials["refresh_token"]
        )
        credentials = google.oauth2.credentials.Credentials(access_token)
        storage.put(credentials)

    with open(
            youtube_ssl_url,
            "r") as f:
        doc = f.read()
        ytb = build_from_document(doc, credentials=credentials)

    current_video = get_last_video_id(playlist_id)
    if current_video:
        current_video_id = current_video["video_id"]
        context.bot.send_message(chat_id=chat_id, text=f"Last video ID: {current_video_id}")

        with open(ROOT_DIR+"/Data/data_functions/time_search", "r") as f:
            time_search = int(f.readline())

        index_0 = random.randint(1, 6)
        stop_btn = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton("Stop")]],
            resize_keyboard=True,
            one_time_keyboard=True)
        
        i = 0
        start = time.time()
        while 3*60 >= int(time.time() - start) and not stop:
            if i == 0:
                context.bot.send_message(chat_id=chat_id, text=f"Waiting...", reply_markup=stop_btn)

            new_video_id = get_last_video_id(playlist_id)
            video_info = new_video_id.get("video_id")

            i += 1
            if video_info != current_video_id:
                context.bot.send_message(chat_id=chat_id, text=f"New video detected! ID: {video_info}")
                insert_comment(ytb, video_info, comment)
                context.bot.send_message(chat_id=chat_id, text=f"Comment wrote: {comment}")
                break
            if time_search != index_0:
                time.sleep(time_search)
            else:
                time.sleep(2)
            if not stop:
                context.bot.send_message(chat_id=chat_id, text=f"Cycle: {i}")
        else:
            if not stop:
                context.bot.send_message(chat_id=chat_id, text="End of cycle", reply_markup=ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton("Cycle again")]],
    resize_keyboard=True,
    one_time_keyboard=True))
    else:
        context.bot.send_message(chat_id=chat_id, text="No current video ID found.",
                                 reply_markup=ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton("Cycle again")]],
    resize_keyboard=True,
    one_time_keyboard=True))


def check_videos(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if access(str(chat_id)):
        playlist_id = user_info[str(chat_id)]["playlist_id"]
        try:
            if access(chat_id):
                remaining_tokens = manage_tokens(chat_id, -1)

                if remaining_tokens > 0:

                    # Schedule the asynchronous checking job
                    job_queue = context.job_queue
                    job_queue.run_once(check_videos_async, 5, context={"playlist_id": playlist_id, "chat_id": chat_id})

                    context.bot.send_message(chat_id=chat_id, text="Checking for new videos in the background...",
                                             reply_markup=ReplyKeyboardRemove())
                    context.bot.send_message(chat_id=chat_id, text=f"You have {remaining_tokens} tokens.")
                else:
                    context.bot.send_message(chat_id=chat_id, text="You don't have enough tokens. Get more to continue.")
        except Exception as e:
            print(f"Error: {e}")
            context.bot.send_message(chat_id=chat_id, text="An error occurred while checking videos.")


def change_channel(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if access(str(chat_id)):
        if len(update.message.text.split()) == 2:
            data = update.message.text.split()
            user_info[str(chat_id)]["playlist_id"] = data[2]
            context.bot.send_message(chat_id=chat_id, text="Your current channel_id was changed")
        else:
            context.bot.send_message(chat_id=chat_id, text="/change_channel channel_id")


def change_comment(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if access(str(chat_id)) and plan_info["name"] in ["Basic", "Premium"]:
        if len(update.message.text.split()) == 2:
            data = update.message.text.split()
            user_info[str(chat_id)]["comment"] = data[2]
            context.bot.send_message(chat_id=chat_id, text="Your current text of comment was changed")
        else:
            context.bot.send_message(chat_id=chat_id, text="/change_comment text")


def change_channel_users(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if str(chat_id) in admin_tg_id:
        if len(update.message.text.split()) == 3:
            data = update.message.text.split()
            user_info[data[1]]["playlist_id"] = data[2]
            context.bot.send_message(chat_id=chat_id, text="edited")
        else:
            context.bot.send_message(chat_id=chat_id, text="/change_channel user_id channel_id")


def set_time_search(update: Update, context: CallbackContext):
    if str(update.message.from_user.id) in admin_tg_id:
        _, time = update.message.text.split()
        if time.isalnum():
            time_search = int(time)
            with open(ROOT_DIR + "Data/data_functions/time_search", "w") as f:
                f.write(str(time_search))
            msg = f"Now default attempts of search is {time_search}"
        else:
            msg = "/set_time_search number"
        context.bot.send_message(chat_id=update.message.from_user.id, text=msg)


def comment_youtube(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if access(chat_id):
        comment = update.message.text
        manage_user_info(chat_id, comnt=comment)
        tutorial_auth(update, context)
        return CHECK_AUTH


def get_playlist_id(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if access(chat_id):
        manage_user_info(chat_id, channel_id=update.message.text)
        context.bot.send_message(chat_id=chat_id, text="Write a comment")
        return COMMENT_YOUTUBE


message_delete = None


def search_warning(update: Update, context: CallbackContext):
    global stop, message_delete
    telegram_user_id = update.effective_chat.id
    if access(telegram_user_id):
        if update.effective_message.text in ["/check_videos", "Start search video", "Cycle again"]:
            stop = False
            message_warning = """
    ⚠️ Warning!
    
    In the next 3 minutes, if video no published, you will lose your 1 token with no use. Do you want to continue?
                """
            inline_btns = InlineKeyboardMarkup([[InlineKeyboardButton(text="Yes", callback_data="Yes"),
                                                 InlineKeyboardButton(text="No", callback_data="No")]])
            message_delete = context.bot.send_message(update.effective_chat.id, message_warning, reply_markup=inline_btns)

        elif update.callback_query:
            data = update.callback_query.data
            if "Yes" in data:
                check_videos(update, context)
            elif "No" in data:
                context.bot.send_message(update.effective_chat.id, message_start,
                                         reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")
            context.bot.edit_message_reply_markup(update.effective_chat.id, message_delete.message_id)


def stop_searching(update: Update, context: CallbackContext):
    telegram_user_id = update.effective_chat.id
    if access(telegram_user_id):
        global stop
        stop = True
        context.bot.send_message(update.effective_chat.id, "Searching stopped",
            reply_markup = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton("Cycle again")]],
            resize_keyboard=True,
            one_time_keyboard=True), parse_mode="HTML")
