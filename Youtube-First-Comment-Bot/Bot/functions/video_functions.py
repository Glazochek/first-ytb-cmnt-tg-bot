import time

import google

from .variables import *
from .another_functions import access
from .tokens_functions import manage_tokens
from .credentials_functions import *
from .auth_functions import tutorial_auth
from .credentials_functions import refresh_token
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

        response = requests.get(url)
        response.raise_for_status()

        video_id = response.json().get("thumbnail_url", "").split("/")[4]
        return {"video_id": video_id} if video_id else None
    except requests.exceptions.RequestException as e:
        print(f"Unable to get playlist information: {e}")
        return None


def check_videos_async(context: CallbackContext):
    global playlist_id, ytb

    chat_id = context.job.context["chat_id"]

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
            "Youtube-First-Comment-Bot/Data/oauth_data/youtube-v3-discoverydocument.json",
            "r") as f:
        doc = f.read()
        ytb = build_from_document(doc, credentials=credentials)

    current_video = get_last_video_id(playlist_id)
    if current_video:
        current_video_id = current_video["video_id"]
        context.bot.send_message(chat_id=chat_id, text=f"Last video ID: {current_video_id}")

        i = 0
        while i != 5:
            new_video_id = get_last_video_id(playlist_id)
            video_info = new_video_id.get("video_id")

            i += 1
            if video_info != current_video_id:
                context.bot.send_message(chat_id=chat_id, text=f"New video detected! ID: {video_info}")
                insert_comment(ytb, video_info, comment)
                context.bot.send_message(chat_id=chat_id, text=f"Comment wrote: {comment}")
                break
            time.sleep(1)
            if i == 1:
                context.bot.send_message(chat_id=chat_id, text=f"Waiting...")
            context.bot.send_message(chat_id=chat_id, text=f"Cycle: {i}")
        else:
            context.bot.send_message(chat_id=chat_id, text="End of cycle")
    else:
        context.bot.send_message(chat_id=chat_id, text="No current video ID found.")


def check_videos(update: Update, context: CallbackContext):
    global playlist_id
    chat_id = update.message.chat_id
    try:
        if access(update.message.from_user.id):
            # if playlist_id[:2] != "UU" and playlist_id[3] == "_":
            #     playlist_id = "UU"+"".join(list(playlist_id)[2:])
            user_id = update.message.from_user.id  # Get the user ID
            remaining_tokens = manage_tokens(user_id, -1)  # Deduct 1 token and get remaining count

            if remaining_tokens > 0:

                # Schedule the asynchronous checking job
                job_queue = context.job_queue
                job_queue.run_once(check_videos_async, 5, context={"playlist_id": playlist_id, "chat_id": chat_id})

                context.bot.send_message(chat_id=chat_id, text="Checking for new videos in the background...")
                context.bot.send_message(chat_id=chat_id, text=f"You have {remaining_tokens} tokens left.")
            else:
                context.bot.send_message(chat_id=chat_id, text="You don't have enough tokens. Get more to continue.")
    except Exception as e:
        print(f"Error: {e}")
        context.bot.send_message(chat_id=chat_id, text="An error occurred while checking videos.")


def comment_youtube(update: Update, context: CallbackContext):
    global comment
    comment = update.message.text
    tutorial_auth(update, context)


def get_playlist_id(update: Update, context: CallbackContext):
    global playlist_id
    chat_id = update.message.chat_id
    playlist_id = update.message.text
    context.bot.send_message(chat_id=chat_id, text="Write a comment")
    return COMMENT_YOUTUBE


