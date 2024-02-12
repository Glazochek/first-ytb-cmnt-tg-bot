from variables import *
from another_functions import *
from access_functions import access_to, delete_user
from tokens_functions import add_tokens, my_tokens
from video_functions import *
from auth_functions import *



def main():
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    all_commands = [CommandHandler("start", start), CommandHandler("authentication", tutorial_auth),
                    CommandHandler("log_out", log_out),
                    CommandHandler("check_videos", search_warning), CommandHandler("add_tokens", add_tokens),
                    CommandHandler("my_tokens", my_tokens), CommandHandler("see_users", open_db),
                    CommandHandler("change_channel", change_channel), CommandHandler("change_comment", change_comment),
                    CommandHandler("change_user_channel", change_channel_users), CommandHandler("send_msg_users", send_msg_users),
                    CommandHandler("send_msg_user", send_msg_user), CommandHandler("set_time_search", set_time_search),
                    CommandHandler("access_to", access_to), CommandHandler("delete_user", delete_user),
                    MessageHandler(filters.Filters.command, invalid_command)]
    # MessageHandler(filters.Filters.text,  lambda x, y: bot.send_message(x.message.from_user.id, "Incorrect msg, use /start to start"))

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Filters.text("registration"), start_reg)],
        states={
            CHECK_VIDEOS: [MessageHandler(filters.Filters.command, no_commands), MessageHandler(filters.Filters.text & ~filters.Filters.command, get_playlist_id)],
            COMMENT_YOUTUBE: [MessageHandler(filters.Filters.command, no_commands), MessageHandler(filters.Filters.text & ~filters.Filters.command, comment_youtube)],
            CHECK_AUTH: [MessageHandler(filters.Filters.command, no_commands), MessageHandler(filters.Filters.text & ~filters.Filters.command, check_auth)],
        },
        fallbacks=[]
    )

    dp.add_handler(conv_handler)

    dp.add_handler(CallbackQueryHandler(tutorial_auth, pattern="url"))
    dp.add_handler(CallbackQueryHandler(check_auth, pattern="check_auth"))
    dp.add_handler(CallbackQueryHandler(search_warning, pattern="Yes|No"))

    dp.add_handler(MessageHandler(filters.Filters.text("See my plan"), plan))
    dp.add_handler(MessageHandler(filters.Filters.text(["Start search video", "Cycle again"]), search_warning))
    dp.add_handler(MessageHandler(filters.Filters.text(["Stop"]), stop_searching))

    for command in all_commands:
        dp.add_handler(command)


    job_queue = updater.job_queue

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()