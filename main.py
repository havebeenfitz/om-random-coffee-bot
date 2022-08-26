import logging
import handlers
import vars
from telegram.ext import *


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.info('Starting Bot')


if __name__ == '__main__':
    updater = Updater(vars.API_KEY, use_context=True)
    dispatcher = updater.dispatcher

    # Add commands
    dispatcher.add_handler(CommandHandler('start', handlers.start_command))
    dispatcher.add_handler(CommandHandler('interview', handlers.interview_command))
    dispatcher.add_handler(CommandHandler('match', handlers.match_command))
    dispatcher.add_handler(CommandHandler('stop', handlers.stop_command))

    # Add message handler
    dispatcher.add_handler(MessageHandler(Filters.text, handlers.handle_message))

    # Add error handler
    dispatcher.add_error_handler(handlers.error)

    updater.start_polling(1.0)
    updater.idle()