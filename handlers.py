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
    print(update.message.text)


# Common handlers
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f'User ({update.message.chat_id}) said {update.message.text}')

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=update.message.text
    )


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f'Update {update} caused error {context.error}')

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Error occured"
    )
