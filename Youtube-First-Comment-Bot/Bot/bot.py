from functions.variables import *
from functions.another_functions import *
from functions.access_functions import *
from functions.tokens_functions import *
from functions.video_functions import *



def main():
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Filters.text("registration"), start_reg)],
        states={
            CHECK_VIDEOS: [MessageHandler(filters.Filters.text & ~filters.Filters.command, get_playlist_id)],
            COMMENT_YOUTUBE: [MessageHandler(filters.Filters.text & ~filters.Filters.command, comment_youtube)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("authentication", tutorial_auth))
    dp.add_handler(CommandHandler("checkvideos", check_videos))
    dp.add_handler(CommandHandler("add_tokens", add_tokens))
    dp.add_handler(CommandHandler("my_tokens", my_tokens))
    dp.add_handler(CommandHandler("open_access", open_access))
    dp.add_handler(CommandHandler("see_users", open_db))

    dp.add_handler(MessageHandler(filters.Filters.text("See my plan"), plan))
    dp.add_handler(MessageHandler(filters.Filters.text(
        [f"Start search video ({i})" for i in range(1, 6)]+["Start search video ({♾️})"]
    ), check_videos))
    dp.add_handler(CallbackQueryHandler(tutorial_auth, pattern="url"))

    dp.add_handler(conv_handler)

    job_queue = updater.job_queue

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    p1 = Process(target=main)
    p1.start()
    p2 = Process(target=serve(app, host="localhost", port=5000))
    p2.start()
