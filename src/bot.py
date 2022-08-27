import logging
from vars import API_KEY
from handlers import *
from models import Command, SurveyState, Gender, MeetingFormat
from telegram.ext import filters, ApplicationBuilder, CommandHandler, MessageHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.info('Starting Bot')


def main():
    application = ApplicationBuilder().token(API_KEY).build()

    # Add handlers
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler(Command.start, start_handler)],
        states={
            SurveyState.gender: [
                MessageHandler(
                    filters.Regex(f"^({Gender.male}|{Gender.female}|{Gender.other})$"),
                    gender_handler
                )
            ],
            SurveyState.meeting_format: [
                MessageHandler(
                    filters.Regex(f"^({MeetingFormat.online}|{MeetingFormat.offline})$"),
                    meeting_format_handler
                )
            ],
            SurveyState.city: [
                MessageHandler(filters.TEXT, city_handler)
            ],
            SurveyState.bio: [
                MessageHandler(filters.TEXT, bio_handler)
            ]
        },
        fallbacks=[
            CommandHandler(Command.cancel, cancel_handler)
        ],
    )
    application.add_handler(conversation_handler)
    application.add_error_handler(error_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
