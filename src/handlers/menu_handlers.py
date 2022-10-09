from telegram import (
    error,
    ChatMember,
    ChatMemberBanned,
    ChatMemberLeft,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler

from src.handlers.common_handlers import *
from src.handlers.pair_handlers import *
from src.models.static_models import Command, MenuCallback, FeedbackCallback, RemoveProfileCallback
from src.vars import ADMIN_ACCOUNTS, FEEDBACK_CHAT_ID

logging.getLogger().setLevel('INFO')
db_helper = DBHelper()

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logging.info('Getting chat member..')
        member = await _get_chat_member(update, context)
        logging.info('Done..')

        if (member is not None) and (member.status is not (ChatMember.LEFT or ChatMember.BANNED)):
            logging.info('Member is fine, show keyboard..')
            db_user = _get_db_user(update, context)

            if db_user is None:
                await update.message.reply_text(
                    text="Привет, я Random Coffee bot!\n\n"
                    "Чтобы начать, заполни профиль ниже. Еще можно временно остановить участие и оставить отзыв",
                )

                menu_markup = _menu_buttons(context, member, db_user)

                await update.message.reply_text(
                    text='Меню',
                    reply_markup=menu_markup
                )
            else:
                await update.message.reply_text(
                    text="Ты уже стартовал, вызови /menu, чтобы заполнить или отредактировать профиль"
                )
        else:
            logging.info('Sending membership message request...')
            await send_membership_message(update, context)
            logging.info('Done')
    except error.BadRequest as e:
        logging.info('Bad request')
        logging.info(e)
        await send_membership_message(update, context)


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logging.info('Getting chat member..')
        member = await _get_chat_member(update, context)
        logging.info('Done..')

        if (member is not None) and (member.status is not (ChatMember.LEFT or ChatMember.BANNED)):
            logging.info('Member is fine, show keyboard..')
            db_user = _get_db_user(update, context)
            reply_keyboard_markup = _menu_buttons(context, member, db_user)

            await update.message.reply_text(
                'Меню',
                reply_markup=reply_keyboard_markup
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
    query = update.callback_query
    await query.answer()

    logging.info('Setting pause on/off')

    db_user = _get_db_user(update, context)

    should_pause = not db_user.is_paused
    db_user.is_paused = should_pause
    context.user_data['is_paused'] = db_user.is_paused

    member = await _get_chat_member(update, context)

    db_helper.pause_user(should_pause, db_user)
    inline_markup = _menu_buttons(context, member, db_user)

    await update.effective_message.edit_reply_markup(inline_markup)

    await update.effective_message.reply_text(
        text='Скрыл твою анкету. Если захочешь участвовать снова, сними с паузы' if should_pause
        else 'Открыл твою анкету, ты снова участвуешь'
    )

    logging.info('Done pause')


async def feedback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    await context.bot.send_message(
        chat_id=user_id,
        text='Напиши, что можно улучшить, я передам'
    )

    return FeedbackCallback.send


async def confirm_remove_profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Надо", callback_data=RemoveProfileCallback.remove)],
        [InlineKeyboardButton("И правда не надо", callback_data=RemoveProfileCallback.cancel)]
    ]

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Может не надо?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def remove_profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    db_helper.delete_user(user_id)

    await update.effective_message.edit_reply_markup(None)
    await update.effective_message.edit_text('Удалил. Заходи еще')

async def cancel_remove_profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await update.effective_message.edit_reply_markup(None)
    await update.effective_message.edit_text('Отменил')

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
             'Если уже подписан, то вступи в ОМ: Флудилка'
    )

    return ConversationHandler.END


# Private

def _get_db_user(update, context) -> User:
    current_db_user = db_helper.get_user(str(update.effective_user.id))

    if current_db_user is not None:
        context.user_data['is_paused'] = current_db_user.is_paused

    return current_db_user


async def _get_chat_member(update, context) -> ChatMember:
    chat_member = await context.bot.get_chat_member(chat_id=MEMBERSHIP_CHAT_ID, user_id=update.effective_user.id)

    return chat_member


def _menu_buttons(context, member, db_user) -> InlineKeyboardMarkup:
    reply_keyboard: list[list[InlineKeyboardButton]] = []

    if db_user is not None:
        reply_keyboard.append(
            [InlineKeyboardButton('👤 Редактировать профиль', callback_data=MenuCallback.fill_profile)]
        )

        if not db_user.is_paused:
            reply_keyboard.append(
                [InlineKeyboardButton(text='⏸️ Поставить на паузу', callback_data=MenuCallback.pause)]
            )
        else:
            reply_keyboard.append(
                [InlineKeyboardButton(text='▶️ Снять с паузы', callback_data=MenuCallback.pause)]
            )

        reply_keyboard.append(
            [InlineKeyboardButton(text='💡 Отправить отзыв', callback_data=MenuCallback.send_feedback)]
        )

        reply_keyboard.append(
            [InlineKeyboardButton(text='❌ Удалить профиль', callback_data=RemoveProfileCallback.confirm)]
        )
    else:
        reply_keyboard.append(
            [InlineKeyboardButton('👤 Заполнить профиль', callback_data=MenuCallback.fill_profile)]
        )

    if str(member.user.id) in ADMIN_ACCOUNTS:
        logging.info(f'{member.user.id} is admin. adding generate pairs handler...')
        reply_keyboard.append(
            [InlineKeyboardButton(text='🎲 Сгенерировать пары', callback_data=MenuCallback.generate_pairs)]
        )
        context.application.add_handler(
            CallbackQueryHandler(callback=generate_pairs_handler, pattern=f"{MenuCallback.generate_pairs}")
        )

    return InlineKeyboardMarkup(inline_keyboard=reply_keyboard)
