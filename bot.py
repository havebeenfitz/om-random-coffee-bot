import json
import logging
import asyncio

from telegram.ext import (
    ApplicationBuilder,
    Application,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    AIORateLimiter
)

from src.handlers.profile_handlers import *
from src.handlers.common_handlers import *
from src.models import Command, SurveyState, Gender, MeetingFormat
from src.vars import TELEGRAM_API_KEY, PROD, TELEGRAM_API_DEBUG_KEY

# Logger setup
logging.getLogger().setLevel('INFO')
logging.info('Starting bot')

application = Application.builder() \
    .token(TELEGRAM_API_KEY if PROD else TELEGRAM_API_DEBUG_KEY) \
    .rate_limiter(AIORateLimiter(overall_max_rate=25)) \
    .build()


def lambda_handler(event, context):
    result = asyncio.get_event_loop().run_until_complete(main(event, context))

    return {
        'statusCode': 200,
        'body': result
    }


async def main(event, context):
    application.add_handler(build_conversation_handler())
    application.add_error_handler(error_handler)

    if PROD:
        logging.info('Start processing response')
        try:
            logging.info('Trying process update')
            await application.initialize()
            await application.process_update(
                Update.de_json(json.loads(event["body"]), application.bot)
            )
            return 'Success'

        except Exception as exc:
            logging.info(f"failed process update with {exc}")

        return 'Failure'

def debug_main():
    conversation_handler = build_conversation_handler()

    application.add_handler(conversation_handler)
    application.add_error_handler(error_handler)

    application.run_polling()


def build_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CommandHandler(Command.start, start_handler)
        ],
        states={
            SurveyState.gender: [
                CallbackQueryHandler(
                    gender_handler,
                    pattern=f"^{Gender.male.id}|{Gender.female.id}|{Gender.other.id}$",
                ),
                CommandHandler(Command.cancel, cancel_handler)
            ],
            SurveyState.meeting_format: [
                CallbackQueryHandler(
                    meeting_format_handler,
                    pattern=f"^({MeetingFormat.online.id}|{MeetingFormat.offline.id})$"
                ),
                CommandHandler(Command.cancel, cancel_handler)
            ],
            SurveyState.city: [
                MessageHandler(filters=filters.LOCATION & ~filters.COMMAND, callback=city_handler),
                CommandHandler(Command.cancel, cancel_handler)
            ],
            SurveyState.bio: [
                MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=bio_handler),
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
