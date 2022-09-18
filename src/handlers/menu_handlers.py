import logging

from telegram import (
    error,
    ChatMemberBanned,
    ChatMemberLeft,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler

from src.handlers.pair_handlers import *
from src.models.static_models import MenuCallback, FeedbackCallback
from src.vars import ADMIN_ACCOUNTS, FEEDBACK_CHAT_ID

logging.getLogger().setLevel('INFO')
db_helper = DBHelper()

current_session_user: User


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logging.info('Getting chat member..')
        member = await context.bot.get_chat_member(chat_id=MEMBERSHIP_CHAT_ID, user_id=update.effective_user.id)
        logging.info('Done..')

        if member.status is not (ChatMemberLeft or ChatMemberBanned):
            logging.info('Member is fine, show keyboard..')
            db_user = db_helper.get_user(user_id=member.user.id)

            reply_keyboard: list[list] = []

            if db_user is not None:
                _add_existing_user_buttons(context, member, db_user, reply_keyboard)
            else:
                reply_keyboard.append(
                    [InlineKeyboardButton('👤 Заполнить профиль', callback_data=MenuCallback.fill_profile)]
                )

            await update.message.reply_text(
                "Привет, я Random Coffee bot!\n\n"
                "Чтобы начать, заполни профиль ниже. Еще можно временно остановить участие и оставить отзыв",
                reply_markup=InlineKeyboardMarkup(reply_keyboard)
            )

            logging.info('Keyboard shown')
        else:
            logging.info('Sending membership message request...')
            await send_membership_message(update, context)
            logging.info('Done')
    except error.BadRequest:
        logging.info('Bad request')
        await send_membership_message(update, context)


async def pause_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info('Setting pause on/off')

    global current_session_user

    try:
        current_session_user
    except NameError:
        current_session_user = db_helper.get_user(str(update.effective_user.id))

    should_pause = not current_session_user.is_paused
    current_session_user.is_paused = should_pause

    db_helper.pause_user(should_pause, current_session_user)
    inline_keyboard = update.callback_query.message.reply_markup.inline_keyboard

    for idx, inline_buttons in enumerate(inline_keyboard):
        if inline_buttons[0].callback_data == MenuCallback.pause:
            if not should_pause:
                inline_keyboard[idx] = \
                    [InlineKeyboardButton(text='⏸️ Поставить на паузу', callback_data=MenuCallback.pause)]
            else:
                inline_keyboard[idx] = \
                    [InlineKeyboardButton(text='▶️ Снять с паузы', callback_data=MenuCallback.pause)]
            break

    await update.callback_query.message.edit_reply_markup(
        InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    )

    logging.info('Done pause')


async def feedback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id

    await context.bot.send_message(
        chat_id=user_id,
        text='Напиши, что можно улучшить, я передам'
    )

    return FeedbackCallback.send


async def send_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = 'Оставили новый отзыв:\n\n' + '__________________\n\n' + update.message.text

    await context.bot.send_message(
        chat_id=FEEDBACK_CHAT_ID,
        text=message
    )
    await context.bot.send_message(chat_id=update.effective_user.id, text='Отправлено, спасибо!')

    return ConversationHandler.END


async def generate_pairs_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await generate_pairs(update, context)


async def send_membership_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        text='Надо быть в стае, чтобы пользоваться ботом. Сходи сюда и подпишись: https://boosty.to/m0rtymerr'
    )

    return ConversationHandler.END


# Private

def _add_existing_user_buttons(context, member, db_user, reply_keyboard_markup):
    context.user_data['is_paused'] = db_user.is_paused
    global current_session_user
    current_session_user = db_user

    reply_keyboard_markup.append(
        [InlineKeyboardButton('👤 Редактировать профиль', callback_data=MenuCallback.fill_profile)]
    )

    if not db_user.is_paused:
        reply_keyboard_markup.append(
            [InlineKeyboardButton(text='⏸️ Поставить на паузу', callback_data=MenuCallback.pause)]
        )
    else:
        reply_keyboard_markup.append(
            [InlineKeyboardButton(text='▶️ Снять с паузы', callback_data=MenuCallback.pause)]
        )

    if str(member.user.id) in ADMIN_ACCOUNTS:
        logging.info(f'{member.user.id} is admin. adding generate pairs handler...')
        reply_keyboard_markup.append(
            [InlineKeyboardButton(text='🎲 Сгенерировать пары', callback_data=MenuCallback.generate_pairs)]
        )
        context.application.add_handler(
            CallbackQueryHandler(callback=generate_pairs_handler, pattern=f"{MenuCallback.generate_pairs}")
        )

    reply_keyboard_markup.append(
        [InlineKeyboardButton(text='💡 Отправить отзыв', callback_data=MenuCallback.send_feedback)]
    )
