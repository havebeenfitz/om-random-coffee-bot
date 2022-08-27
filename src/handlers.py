import logging
from vars import TELEGRAM_API_KEY, OM_FLOOD_CHAT_ID, OM_USEFUL_CHAT_ID
from db_manager import *
from models import SurveyState, Gender, MeetingFormat
from telegram.ext import ContextTypes, ConversationHandler
from telegram import (
    Update,
    Bot,
    KeyboardButton,
    KeyboardButtonPollType,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)

# Logger setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# DB connection
db_manager = DBManager()


# Conversation handlers
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> SurveyState:
    db_manager.restart()
    bot = Bot(token=TELEGRAM_API_KEY)
    member = await bot.get_chat_member(
        chat_id=OM_FLOOD_CHAT_ID,
        user_id=update.effective_user.id
    )

    if not member:
        return await context.bot.send_message(
            chat_id=update.effective_user.id,
            text='Надо быть в стае, чтобы пользоваться ботом. Сходи сюда и подпишись: https://boosty.to/m0rtymerr'
        )

    else:
        reply_keyboard = [
            [KeyboardButton(text=Gender.male), KeyboardButton(text=Gender.female)],
            [KeyboardButton(text=Gender.other)]
        ]

        await update.message.reply_text(
            "Алоха! Расскажи немного о себе, и я подберу человека из стаи.\n"
            "Кто ты?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                resize_keyboard=True,
                selective=True,
                input_field_placeholder="Выбери гендерную принадлежность"
            ),
        )

        db_manager.add_user(
            user_id=member.user.id,
            username=member.user.username
        )

        return SurveyState.gender


async def gender_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> SurveyState:
    gender_text = update.message.text
    user = update.message.from_user
    context.user_data['gender'] = gender_text

    logger.info("Gender of %s: %s", user.first_name, gender_text)

    reply_keyboard = [[MeetingFormat.online, MeetingFormat.offline]]
    markup = ReplyKeyboardMarkup(
        reply_keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "Ок, "
        "Хочешь поболтать онлайн или в офлайне?",
        reply_markup=markup,
    )

    return SurveyState.meeting_format


async def meeting_format_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> SurveyState:
    meet_format = update.message.text
    user = update.message.from_user.name
    context.user_data['meeting_format'] = meet_format

    logger.info("Meeting format of %s: %s", user, update.message.text)

    if meet_format == MeetingFormat.offline:
        await update.message.reply_text(
            text="Где ты живешь? Формат: Страна, город",
            reply_markup=ReplyKeyboardRemove()
        )
        return SurveyState.city
    else:
        await update.message.reply_text(
            text="Коротко напиши о своих интересах",
            reply_markup=ReplyKeyboardRemove()
        )
        return SurveyState.bio


async def city_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> SurveyState:
    city_text = update.message.text
    user_name = update.message.from_user.name
    context.user_data['city'] = city_text

    logger.info("City of %s: %s", user_name, city_text)

    await update.message.reply_text(text="Коротко напиши о своих интересах в произвольной форме")

    return SurveyState.bio


async def bio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    bio_text = update.message.text
    user_name = update.message.from_user.name
    context.user_data['city'] = bio_text

    logger.info("Bio of %s: %s", user_name, bio_text)
    db_manager.stop()

    await update.message.reply_text(
        text="Спасибо! Запускаем казино по понедельникам в течение дня...."
    )

    return ConversationHandler.END


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)

    await update.message.reply_text(
        "Ну ты это, заходи еще",
        reply_markup=ReplyKeyboardRemove()
    )

    db_manager.stop()

    return ConversationHandler.END


# Common handlers
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f'Update {update} caused error {context.error}')

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Одна ошибка и ты ошибся: {context.error}'
    )
