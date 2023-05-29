import logging
from typing import Optional, Tuple

from telegram import Update, Chat, ChatMember, ChatMemberUpdated
from telegram.ext import ConversationHandler, ContextTypes

from src.db_helper import DBHelper

# Logger setup

logging.getLogger().setLevel('INFO')

# Common handlers

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logging.info("User %s canceled the conversation.", user.first_name)

    await context.bot.send_message(chat_id=update.message.from_user.id, text="Ну ты это, заходи еще")

    return ConversationHandler.END


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f'Update {update} caused error {context.error}')

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Одна ошибка и ты ошибся: {context.error}'
    )
