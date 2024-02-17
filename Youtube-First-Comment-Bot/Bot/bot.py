from variables import *
from another_functions import *
from access_functions import access_to, delete_user
from tokens_functions import add_tokens, my_tokens
from video_functions import *
from auth_functions import *
from credentials_functions import get_user_cred


def main():
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    all_commands = [CommandHandler("start", start, run_async=True), CommandHandler("authentication", tutorial_auth, run_async=True),
                    CommandHandler("log_out", log_out, run_async=True),
                    CommandHandler("check_videos", search_warning, run_async=True), CommandHandler("add_tokens", add_tokens, run_async=True),
                    CommandHandler("my_tokens", my_tokens, run_async=True), CommandHandler("see_users", open_db, run_async=True),
                    CommandHandler("change_channel", change_channel, run_async=True), CommandHandler("change_comment", change_comment, run_async=True),
                    CommandHandler("change_user_channel", change_channel_users, run_async=True), CommandHandler("send_msg_users", send_msg_users, run_async=True),
                    CommandHandler("send_msg_user", send_msg_user, run_async=True), CommandHandler("set_time_search", set_time_search, run_async=True),
                    CommandHandler("get_user_cred", get_user_cred, run_async=True),CommandHandler("access_to", access_to, run_async=True),
                    CommandHandler("delete_user", delete_user, run_async=True),
                    MessageHandler(filters.Filters.command, invalid_command, run_async=True)]

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Filters.text("registration"), start_reg)],
        states={
            CHECK_VIDEOS: [MessageHandler(filters.Filters.command, no_commands, run_async=True), MessageHandler(filters.Filters.text & ~filters.Filters.command, get_playlist_id, run_async=True)],
            COMMENT_YOUTUBE: [MessageHandler(filters.Filters.command, no_commands, run_async=True), MessageHandler(filters.Filters.text & ~filters.Filters.command, comment_youtube, run_async=True)],
            CHECK_AUTH: [MessageHandler(filters.Filters.command, no_commands, run_async=True), MessageHandler(filters.Filters.text & ~filters.Filters.command, check_auth, run_async=True)],
        },
        fallbacks=[]
    )

    dp.add_handler(conv_handler)

    dp.add_handler(CallbackQueryHandler(tutorial_auth, pattern="url", run_async=True))
    dp.add_handler(CallbackQueryHandler(check_auth, pattern="check_auth", run_async=True))
    dp.add_handler(CallbackQueryHandler(search_warning, pattern="Yes|No", run_async=True))

    dp.add_handler(MessageHandler(filters.Filters.text("See my plan"), plan, run_async=True))
    dp.add_handler(MessageHandler(filters.Filters.text(["Start search video", "Cycle again"]), search_warning, run_async=True))
    dp.add_handler(MessageHandler(filters.Filters.text(["Stop"]), stop_searching, run_async=True))

    for command in all_commands:
        dp.add_handler(command)

    job_queue = updater.job_queue

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()