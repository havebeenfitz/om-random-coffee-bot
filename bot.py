import json
import logging
import asyncio

from telegram.ext import (
    filters,
    ApplicationBuilder,
    Application,
    ContextTypes,
    ChatMemberHandler,
    CommandHandler,
    CallbackQueryHandler,
    AIORateLimiter,
    MessageHandler
)

from src.handlers.menu_handlers import *
from src.handlers.profile_handlers import *
from src.handlers.common_handlers import *
from src.models.static_models import (
    Command, FillProfileCallback, FeedbackCallback, GenderCallback, MeetingFormatCallback
)
from src.vars import TELEGRAM_API_KEY, PROD, TELEGRAM_API_DEBUG_KEY

# Logger setup
logging.getLogger().setLevel('INFO')
logging.info('Starting bot')

application = Application.builder() \
    .token(TELEGRAM_API_KEY if PROD else TELEGRAM_API_DEBUG_KEY) \
    .rate_limiter(AIORateLimiter(overall_max_rate=25)) \
    .build()


def user_lambda_handler(event, context):
    result = asyncio.get_event_loop().run_until_complete(main(event, context))

    return {
        'statusCode': 200,
        'body': result
    }

async def main(event, context):
    add_user_handlers()

    if PROD:
        return await handle_update(event)

async def handle_update(event):
    try:
        logging.info('Processing update...')
        await application.initialize()
        await application.process_update(
            Update.de_json(json.loads(event["body"]), application.bot)
        )
        logging.info(f'Processed update {event["body"]}')
        return 'Success'

    except Exception as exc:
        logging.info(f"Failed to process update with {exc}")
    return 'Failure'

def debug_main():
    add_user_handlers()

    application.run_polling()

def add_user_handlers():
    # Track commands
    application.add_handler(
        CommandHandler(command=Command.start, callback=start_handler, filters=filters.ChatType.PRIVATE)
    )
    application.add_handler(
        CommandHandler(command=Command.menu, callback=menu_handler, filters=filters.ChatType.PRIVATE)
    )

    # Track Conversations and callbacks

    application.add_handler(profile_conversation_handler())
    application.add_handler(CallbackQueryHandler(callback=pause_handler, pattern=f"^{MenuCallback.pause}$"))
    application.add_handler(feedback_conversation_handler())

    # Track Remove profile with confirmation
    application.add_handler(
        CallbackQueryHandler(confirm_remove_profile_handler, pattern=f"^{RemoveProfileCallback.confirm}$")
    )
    application.add_handler(
        CallbackQueryHandler(remove_profile_handler, pattern=f"^{RemoveProfileCallback.remove}$")
    )
    application.add_handler(
        CallbackQueryHandler(cancel_remove_profile_handler, pattern=f"^{RemoveProfileCallback.cancel}$")
    )

    # Track start/block actions
    application.add_handler(ChatMemberHandler(callback=track_chats))

    # Track errors
    application.add_error_handler(error_handler)

def profile_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                profile_handler,
                pattern=f"^{MenuCallback.fill_profile}$"
            ),
            CommandHandler(Command.cancel, cancel_handler)
        ],
        states={
            FillProfileCallback.gender: [
                CallbackQueryHandler(
                    gender_handler,
                    pattern=f"^{GenderCallback.male.id}|{GenderCallback.female.id}|{GenderCallback.other.id}$",
                ),
                CommandHandler(Command.cancel, cancel_handler)
            ],
            FillProfileCallback.meeting_format: [
                CallbackQueryHandler(
                    meeting_format_handler,
                    pattern=f"^({MeetingFormatCallback.online.id}|{MeetingFormatCallback.offline.id})$"
                ),
                CommandHandler(Command.cancel, cancel_handler)
            ],
            FillProfileCallback.city: [
                MessageHandler(filters=filters.LOCATION & ~filters.COMMAND & ~filters.TEXT, callback=city_handler),
                CommandHandler(Command.cancel, cancel_handler)
            ],
            FillProfileCallback.bio: [
                MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=bio_handler),
                CommandHandler(Command.cancel, cancel_handler)
            ]
        },
        fallbacks=[
            CommandHandler(Command.cancel, cancel_handler)
        ]
    )


def feedback_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                feedback_handler,
                pattern=f"^{MenuCallback.send_feedback}$"
            ),
            CommandHandler(Command.cancel, cancel_handler)
        ],
        states={
            FeedbackCallback.send: [
                MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=send_feedback),
                CommandHandler(Command.cancel, cancel_handler)
            ]
        },
        fallbacks=[
            CommandHandler(Command.cancel, cancel_handler)
        ]
    )


if __name__ == '__main__':
    if not PROD:
        debug_main()
