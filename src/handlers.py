import logging
import reverse_geocoder as rg
from src.vars import MEMBERSHIP_CHAT_ID
from src.models import SurveyState, Gender, MeetingFormat
from telegram.ext import CallbackContext, ConversationHandler
from telegram import (
    ChatAction,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton
)

# Logger setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Conversation handlers
def start_handler(update: Update, context: CallbackContext) -> int:
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    member = context.bot.get_chat_member(
        chat_id=MEMBERSHIP_CHAT_ID,
        user_id=update.effective_user.id
    )

    if not member:
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text='Надо быть в стае, чтобы пользоваться ботом. Сходи сюда и подпишись: https://boosty.to/m0rtymerr'
        )

        return ConversationHandler.END
    else:
        reply_keyboard = [
            [
                InlineKeyboardButton(text=Gender.male.text, callback_data=Gender.male.id),
                InlineKeyboardButton(text=Gender.female.text, callback_data=Gender.female.id)
            ],
            [
                InlineKeyboardButton(text=Gender.other.text, callback_data=Gender.other.id)
            ]
        ]

        update.message.reply_text(
            "Алоха! Расскажи немного о себе, и я подберу человека из стаи.\n\n"
            "Кто ты?",
            reply_markup=InlineKeyboardMarkup(
                reply_keyboard
            ),
        )

        return SurveyState.gender


def gender_handler(update: Update, context: CallbackContext) -> SurveyState:
    query = update.callback_query
    query.answer()

    logger.info("Gender of %s: %s", update.effective_user.username, update.callback_query.data)

    reply_keyboard = [
        [
            InlineKeyboardButton(MeetingFormat.online.text, callback_data=MeetingFormat.online.id),
            InlineKeyboardButton(MeetingFormat.offline.text, callback_data=MeetingFormat.offline.id)
        ]
    ]
    markup = InlineKeyboardMarkup(reply_keyboard)

    query.edit_message_text(
        "Ок, Хочешь поболтать онлайн или в офлайне?",
        reply_markup=markup,
    )

    return SurveyState.meeting_format


def meeting_format_handler(update: Update, context: CallbackContext) -> SurveyState:
    query = update.callback_query
    query.answer()

    logger.info("Meeting format: %s", update.callback_query.data)

    if query.data == MeetingFormat.offline.id:
        new_keyboard = [[KeyboardButton(text='Поделиться локацией', request_location=True)]]
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text='Где ты находишься? В локации будут использованы только страна и город',
            reply_markup=ReplyKeyboardMarkup(new_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return SurveyState.city
    else:
        query.edit_message_text(
            text="Коротко напиши о своих интересах",
        )
        return SurveyState.bio


def city_handler(update: Update, context: CallbackContext) -> SurveyState:
    update.message.reply_text(
        text='Вычленяем страну и город, абажди...',
        reply_markup=ReplyKeyboardRemove()
    )
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    coordinates = (update.message.location.latitude, update.message.location.longitude)
    location = rg.get(coordinates)

    logger.info(f"{location['cc']}")
    logger.info(f"{location['name']}")

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Коротко напиши о своих интересах в произвольной форме",
        reply_markup=ReplyKeyboardRemove()
    )

    return SurveyState.bio


def bio_handler(update: Update, context: CallbackContext) -> int:
    logger.info(update.message.text)
    update.message.reply_text(
        text="Спасибо! Запускаем казино по понедельникам в течение дня...."
    )

    return ConversationHandler.END


# Common handlers
def cancel_handler(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)

    context.bot.send_message(chat_id=update.message.from_user.id, text="Ну ты это, заходи еще")

    return ConversationHandler.END


def error_handler(update: Update, context: CallbackContext):
    logging.error(f'Update {update} caused error {context.error}')

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Одна ошибка и ты ошибся: {context.error}'
    )
