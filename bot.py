import json
import logging

from telegram.ext import (
    ApplicationBuilder,
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

application = ApplicationBuilder()\
    .token(TELEGRAM_API_KEY if PROD else TELEGRAM_API_DEBUG_KEY)\
    .rate_limiter(AIORateLimiter(overall_max_rate=25))\
    .build()

logging.info('Starting bot')


def main(event, context):
    conversation_handler = ConversationHandler(
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

    application.add_handler(conversation_handler)
    application.add_error_handler(error_handler)

    if PROD:
        logging.info('Start processing response')
        try:
            logging.info('Trying process update')
            application.process_update(
                Update.de_json(json.loads(event["body"]), application.bot)
            )

        except Exception as exc:
            logging.info(f"failed process update with {exc}")
            return {
                "statusCode": 500
            }

        return {
            "statusCode": 200
        }
    else:
        logging.info('Start polling...')
        application.run_polling()


if __name__ == '__main__':
    if not PROD:
        main(None, None)
