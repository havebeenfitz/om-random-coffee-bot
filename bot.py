import json

from telegram.ext import Updater, CallbackQueryHandler
from telegram.ext import messagequeue as mq
from telegram.utils.request import Request

from src.subclasses.rate_limited_bot import MQBot

from src.handlers.profile_handlers import *
from src.handlers.common_handlers import *
from src.models import Command, SurveyState, Gender, MeetingFormat
from src.vars import TELEGRAM_API_KEY, PROD, TELEGRAM_API_DEBUG_KEY

# Logger setup
logging.getLogger().setLevel('INFO')

queue = mq.MessageQueue(all_burst_limit=25)
request = Request()
bot = MQBot(TELEGRAM_API_KEY if PROD else TELEGRAM_API_DEBUG_KEY, request=request, mqueue=queue)
updater = Updater(bot=bot)
dispatcher = updater.dispatcher

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
                MessageHandler(filters=Filters.location & ~Filters.command, callback=city_handler),
                CommandHandler(Command.cancel, cancel_handler)
            ],
            SurveyState.bio: [
                MessageHandler(filters=Filters.text & ~Filters.command, callback=bio_handler),
                CommandHandler(Command.cancel, cancel_handler)
            ]
        },
        fallbacks=[
            CommandHandler(Command.cancel, cancel_handler)
        ]
    )

    dispatcher.add_handler(conversation_handler)
    dispatcher.add_error_handler(error_handler)

    if PROD:
        try:
            dispatcher.process_update(
                Update.de_json(json.loads(event["body"]), bot)
            )

        except Exception as e:
            logging.info(e)
            return {
                "statusCode": 500
            }

        return {
            "statusCode": 200
        }
    else:
        updater.start_polling()
        updater.idle()
        logging.info('Updater idle...')


if __name__ == '__main__':
    if not PROD:
        main(None, None)
