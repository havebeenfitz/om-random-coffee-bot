import logging
from handlers import *
import vars
from models import SurveyState
from telegram.ext import filters, ApplicationBuilder, CommandHandler, MessageHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.info('Starting Bot')


def main():
    application = ApplicationBuilder().token(vars.API_KEY).build()

    # Add handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SurveyState.gender: [
                MessageHandler(filters.Regex("^(Муж|Дама|Другое)$"), gender)
            ],
            SurveyState.meeting_format: [
                MessageHandler(filters.Regex("^(Онлайн|Оффлайн)$"), meeting_format)
            ],
            SurveyState.city: [
                MessageHandler(filters.TEXT, city)
            ],
            SurveyState.bio: [
                MessageHandler(filters.TEXT, bio)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
    )
    # application.add_handler(MessageHandler(filters.TEXT, handlers.handle_message))
    application.add_handler(conv_handler)
    application.add_error_handler(error)

    application.run_polling()


if __name__ == '__main__':
    main()
