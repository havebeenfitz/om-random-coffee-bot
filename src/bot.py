import logging
import handlers
import vars
from telegram.ext import filters, ApplicationBuilder, CommandHandler, MessageHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.info('Starting Bot')


if __name__ == '__bot__':
    application = ApplicationBuilder().token(vars.API_KEY).build()

    # Add handlers
    application.add_handler(CommandHandler('start', handlers.start))
    application.add_handler(CommandHandler('interview', handlers.interview))
    application.add_handler(CommandHandler('match', handlers.match))
    application.add_handler(CommandHandler('stop', handlers.stop))
    application.add_handler(MessageHandler(filters.TEXT, handlers.handle_message))
    application.add_error_handler(handlers.error)

    application.run_polling()
