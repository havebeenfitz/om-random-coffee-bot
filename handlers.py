import logging
from telegram import Update
from telegram.ext import ContextTypes


# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет, волк. Заполни анкету через /interview, после этого запусти казино через /match"
    )


async def interview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Interview. TODO"
    )


async def match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Match. TODO"
    )


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.stopPoll()


# Common handlers
def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = str(update.message.text).lower()
    logging.info(f'User ({update.message.chat_id}) said {text}')

    update.message.reply_text('Заполни анкету через /interview, запусти казино через /match')


def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f'Update {update} caused error {context.error}')