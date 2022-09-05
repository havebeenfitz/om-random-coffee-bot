import logging

from telegram import Update
from telegram.ext import ConversationHandler, CallbackContext

# Logger setup

logging.getLogger().setLevel('INFO')


# Common handlers

def cancel_handler(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logging.info("User %s canceled the conversation.", user.first_name)

    context.bot.send_message(chat_id=update.message.from_user.id, text="Ну ты это, заходи еще")

    return ConversationHandler.END


def error_handler(update: Update, context: CallbackContext):
    logging.error(f'Update {update} caused error {context.error}')

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Одна ошибка и ты ошибся: {context.error}'
    )
