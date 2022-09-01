import json

from telegram.ext import Filters, Updater, CommandHandler, MessageHandler

from src.handlers import *
from src.models import Command, SurveyState, Gender, MeetingFormat
from src.vars import TELEGRAM_API_KEY, PROD, TELEGRAM_API_DEBUG_KEY

# Logger setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
logger.info('Starting bot')

updater = Updater(token=TELEGRAM_API_KEY if PROD else TELEGRAM_API_DEBUG_KEY)
bot = updater.bot
dispatcher = updater.dispatcher


def main(event, context):
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler(Command.start, start_handler)],
        states={
            SurveyState.gender: [
                MessageHandler(
                    Filters.regex(f"^({Gender.male.text}|{Gender.female.text}|{Gender.other.text})$"),
                    gender_handler
                )
            ],
            SurveyState.meeting_format: [
                MessageHandler(
                    Filters.regex(f"^({MeetingFormat.online}|{MeetingFormat.offline})$"),
                    meeting_format_handler
                )
            ],
            SurveyState.city: [
                MessageHandler(Filters.text, city_handler)
            ],
            SurveyState.bio: [
                MessageHandler(Filters.text, bio_handler)
            ]
        },
        fallbacks=[
            CommandHandler(Command.cancel, cancel_handler)
        ],
    )

    dispatcher.add_handler(conversation_handler)

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


if __name__ == '__main__':
    if not PROD:
        main(None, None)
