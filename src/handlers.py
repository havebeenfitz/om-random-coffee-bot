import logging
import vars
from models import SurveyState
from telegram import (
    Update,
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import ContextTypes, ConversationHandler


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> SurveyState:
    bot = Bot(token=vars.API_KEY)
    member = await bot.get_chat_member(
        chat_id=vars.OM_FLOOD_CHAT_ID,
        user_id=update.effective_user.id
    )

    if not member:
        return await context.bot.send_message(
            chat_id=update.effective_user.id,
            text='Надо быть в стае, чтобы пользоваться ботом. Сходи сюда и подпишись: https://boosty.to/m0rtymerr'
        )

    else:
        reply_keyboard = [["Муж", "Дама", "Другое"]]

        await update.message.reply_text(
            "Алоха! Расскажи немного о себе, и я подберу человека из стаи.\n"
            "Кто ты?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True,
                input_field_placeholder="Выбери гендерную принадлежность"
            ),
        )

        return SurveyState.gender


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> SurveyState:
    gender_text = update.message.text
    user = update.message.from_user
    context.user_data['gender'] = gender_text

    logger.info("Gender of %s: %s", user.first_name, gender_text)

    reply_keyboard = [["Онлайн", "Оффлайн"]]
    markup = ReplyKeyboardMarkup(reply_keyboard)

    await update.message.reply_text(
        "Ок,\n"
        "Хочешь поболтать онлайн или в офлайне?",
        reply_markup=markup,
    )

    return SurveyState.meeting_format


async def meeting_format(update: Update, context: ContextTypes.DEFAULT_TYPE) -> SurveyState:
    meet_format = update.message.text
    user = update.message.from_user.name
    context.user_data['meeting_format'] = meet_format

    logger.info("Meeting format of %s: %s", user, update.message.text)

    if meet_format == 'Оффлайн':
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


async def city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> SurveyState:
    city_text = update.message.text
    user_name = update.message.from_user.name
    context.user_data['city'] = city_text

    logger.info("City of %s: %s", user_name, city_text)

    await update.message.reply_text(text="Коротко напиши о своих интересах в произвольной форме")

    return SurveyState.bio


async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> SurveyState:
    bio_text = update.message.text
    user_name = update.message.from_user.name
    context.user_data['city'] = bio_text

    logger.info("Bio of %s: %s", user_name, bio_text)

    await update.message.reply_text(text="Спасибо! Запускаем казино по понедельникам в течение дня....")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Ну ты это, заходи еще", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


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
        text=f'Error occured {context.error}'
    )
