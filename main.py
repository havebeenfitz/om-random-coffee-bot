import logging
import handlers
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler
from telegram.ext.filters import Text

import vars

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.info('Starting Bot')


if __name__ == '__main__':
    application = ApplicationBuilder().token(vars.API_KEY).build()

    # Add commands
    application.add_handler(CommandHandler('start', handlers.start_command))
    application.add_handler(CommandHandler('interview', handlers.interview_command))
    application.add_handler(CommandHandler('match', handlers.match_command))
    application.add_handler(CommandHandler('stop', handlers.stop_command))

    # Add message handler
    application.add_handler(MessageHandler(Text, handlers.handle_message))

    # Add error handler
    application.add_error_handler(handlers.error)

    application.run_polling()