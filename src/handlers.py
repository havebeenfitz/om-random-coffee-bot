import logging
from src.vars import OM_FLOOD_CHAT_ID
from src.models import SurveyState, Gender, MeetingFormat
from telegram.ext import CallbackContext, ConversationHandler
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)

# Logger setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Conversation handlers
def start_handler(update: Update, context: CallbackContext) -> SurveyState:
    member = context.bot.get_chat_member(
        chat_id=OM_FLOOD_CHAT_ID,
        user_id=update.effective_user.id
    )

    if not member:
        return context.bot.send_message(
            chat_id=update.effective_user.id,
            text='Надо быть в стае, чтобы пользоваться ботом. Сходи сюда и подпишись: https://boosty.to/m0rtymerr'
        )

    else:
        reply_keyboard = [
            [KeyboardButton(text=Gender.male.text), KeyboardButton(text=Gender.female.text)],
            [KeyboardButton(text=Gender.other.text)]
        ]

        update.message.reply_text(
            "Алоха! Расскажи немного о себе, и я подберу человека из стаи.\n"
            "Кто ты?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                resize_keyboard=True,
                selective=True,
                input_field_placeholder="Выбери гендерную принадлежность"
            ),
        )

        return SurveyState.gender


def gender_handler(update: Update, context: CallbackContext) -> SurveyState:
    gender_text = update.message.text
    user = update.message.from_user
    context.user_data['gender'] = gender_text

    logger.info("Gender of %s: %s", user.first_name, gender_text)

    reply_keyboard = [[MeetingFormat.online, MeetingFormat.offline]]
    markup = ReplyKeyboardMarkup(
        reply_keyboard,
        resize_keyboard=True
    )

    update.message.reply_text(
        "Ок, "
        "Хочешь поболтать онлайн или в офлайне?",
        reply_markup=markup,
    )

    return SurveyState.meeting_format


def meeting_format_handler(update: Update, context: CallbackContext) -> SurveyState:
    meet_format = update.message.text
    user = update.message.from_user.name
    context.user_data['meeting_format'] = meet_format

    logger.info("Meeting format of %s: %s", user, update.message.text)

    if meet_format == MeetingFormat.offline:
        update.message.reply_text(
            text="Где ты живешь? Формат: Страна, город",
            reply_markup=ReplyKeyboardRemove()
        )
        return SurveyState.city
    else:
        update.message.reply_text(
            text="Коротко напиши о своих интересах",
            reply_markup=ReplyKeyboardRemove()
        )
        return SurveyState.bio


def city_handler(update: Update, context: CallbackContext) -> SurveyState:
    city_text = update.message.text
    user_name = update.message.from_user.name
    context.user_data['city'] = city_text

    logger.info("City of %s: %s", user_name, city_text)

    update.message.reply_text(text="Коротко напиши о своих интересах в произвольной форме")

    return SurveyState.bio


def bio_handler(update: Update, context: CallbackContext) -> int:
    bio_text = update.message.text
    user_name = update.message.from_user.name
    context.user_data['city'] = bio_text

    logger.info("Bio of %s: %s", user_name, bio_text)

    update.message.reply_text(
        text="Спасибо! Запускаем казино по понедельникам в течение дня...."
    )

    return ConversationHandler.END


def cancel_handler(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)

    update.message.reply_text(
        "Ну ты это, заходи еще",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


# Common handlers
def error_handler(update: Update, context: CallbackContext):
    logging.error(f'Update {update} caused error {context.error}')

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Одна ошибка и ты ошибся: {context.error}'
    )
