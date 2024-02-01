from .variables import *

message_tutorial = """
👤 How to Authenticate?

We will use your google account to create comment in youtube

1. You need to choose your google account
2. Click 'additional settings' -> 'Go to the page'
3. Click 'Continue' and return to the telegram bot
"""

keyboard_reply_1 = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton("start searching")]],
    resize_keyboard=True,
    one_time_keyboard=True)


def get_authenticated_service():
    return flow.step1_get_authorize_url()


def tutorial_auth(update: Update, context: CallbackContext):
    if context.job and context.job.callback == "url":
        context.bot.send_message(update.effective_chat.id,
                                 text="Let's start searching new video!",
                                 reply_markup=keyboard_reply_1)
    else:
        url = get_authenticated_service()
        if url:
            context.bot.send_media_group(update.effective_chat.id, media=[
            InputMediaPhoto(open("Youtube-First-Comment-Bot/Data/imgs/1.jpg", "rb").read()),
            InputMediaPhoto(open("Youtube-First-Comment-Bot/Data/imgs/2.jpg", "rb").read()),
            InputMediaPhoto(open("Youtube-First-Comment-Bot/Data/imgs/3.jpg", "rb").read())])
            context.bot.send_message(update.effective_chat.id, message_tutorial, reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Google authentication", url=url, callback_data="url")]]))
        else:
            context.bot.send_message(update.effective_chat.id, text="You already authenticated")
        return ConversationHandler.END


