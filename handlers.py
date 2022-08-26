from telegram.ext import *
import telegram.update
import logging


# Commands

def start_command(update, context):
    update.message.reply_text(
        'Привет, волк. Заполни анкету через /interview, после этого запусти казино через /match'
    )


def interview_command(update, context):
    print()


def match_command(update, context):
    print()


def stop_command(update, context):
    print()

# Common handlers


def handle_message(update: Updater, context: CallbackContext):
    text = str(update.message.text).lower()
    logging.info(f'User ({update.message.chat_id}) said {text}')

    update.message.reply_text('Заполни анкету через /interview, запусти казино через /match')


def error(update, context):
    logging.error(f'Update {update} caused error {context.error}')