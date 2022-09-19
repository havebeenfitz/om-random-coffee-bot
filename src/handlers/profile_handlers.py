from src.vars import GEONAMES_ACCOUNT
from src.models.static_models import FillProfileCallback, GenderCallback, MeetingFormatCallback
from src.handlers.pair_handlers import *

from geopy import GeoNames, Location
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ChatAction
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton
)

# Logger setup
logging.getLogger().setLevel('INFO')

geo = GeoNames(GEONAMES_ACCOUNT)
db_helper = DBHelper()


# Conversation handlers

async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    logging.info('Member is fine, show keyboard..')
    reply_keyboard_markup = [
        [
            InlineKeyboardButton(
                text=GenderCallback.male.text,
                callback_data=GenderCallback.male.id
            ),
            InlineKeyboardButton(
                text=GenderCallback.female.text,
                callback_data=GenderCallback.female.id
            )
        ],
        [
            InlineKeyboardButton(
                text=GenderCallback.other.text,
                callback_data=GenderCallback.other.id
            )
        ]
    ]

    await context.bot.send_message(
        text="Сейчас задам несколько вопросов, чтобы подобрать тебе человека. Кто ты?",
        chat_id=update.effective_user.id,
        reply_markup=InlineKeyboardMarkup(
            reply_keyboard_markup
        ),
    )

    logging.info('Profile edit started')

    return FillProfileCallback.gender


async def gender_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data['gender'] = query.data

    logging.info("Gender of %s: %s", update.effective_user.username, update.callback_query.data)

    reply_keyboard = [
        [
            InlineKeyboardButton(
                MeetingFormatCallback.online.text,
                callback_data=MeetingFormatCallback.online.id
            ),
            InlineKeyboardButton(
                MeetingFormatCallback.offline.text,
                callback_data=MeetingFormatCallback.offline.id
            )
        ]
    ]
    markup = InlineKeyboardMarkup(reply_keyboard)

    await query.edit_message_text(
        "Ок, Хочешь поболтать онлайн или в офлайне?",
        reply_markup=markup,
    )

    return FillProfileCallback.meeting_format


async def meeting_format_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data['format'] = query.data

    logging.info("Meeting format: %s", update.callback_query.data)

    if query.data == MeetingFormatCallback.offline.id:
        new_keyboard = [[KeyboardButton(text='Поделиться локацией', request_location=True)]]
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text='Где ты находишься? Нажми кнопку "Поделиться локацией" снизу. \n\nИз локации будут использованы только страна и город',
            reply_markup=ReplyKeyboardMarkup(new_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return FillProfileCallback.city
    else:
        await query.edit_message_text(
            text="Коротко напиши о своих интересах",
        )
        return FillProfileCallback.bio


async def city_handler(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        text='Вычленяем страну и город, абажди...',
        reply_markup=ReplyKeyboardRemove()
    )
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    coordinates = (update.message.location.latitude, update.message.location.longitude)
    location: Location = geo.reverse(query=coordinates, exactly_one=True, timeout=2)

    country = location.raw['countryCode']
    city = location.raw['adminName1']

    logging.info(f"{country}")
    logging.info(f"{city}")

    context.user_data['country'] = country
    context.user_data['city'] = city

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Коротко напиши о своих интересах в произвольной форме",
        reply_markup=ReplyKeyboardRemove()
    )

    return FillProfileCallback.bio


async def bio_handler(update: Update, context: CallbackContext) -> int:
    bio = update.message.text
    context.user_data['bio'] = bio

    logging.info(f"Bio: {bio}")

    await update_user_in_db(update, context)

    return ConversationHandler.END


async def update_user_in_db(update, context):
    username = update.effective_user.username
    bio = context.user_data['bio']

    if 'city' in context.user_data:
        city = context.user_data['city']

        await update.message.reply_text(
            f"Нойс, @{username}, ты заполнил анкeту!\nХочешь встретиться оффлайн в {city}\nТвои интересы: {bio}"
        )
    else:
        await update.message.reply_text(
            f"Нойс, @{username}, ты заполнил анкeту!\nХочешь поболтать онлайн\nТвои интересы: {bio}"
        )

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    context.user_data['user_id'] = str(update.effective_user.id)
    context.user_data['username'] = update.effective_user.username
    if 'is_paused' not in context.user_data:
        context.user_data['is_paused'] = False

    user = User(user_dict=context.user_data)

    db_helper.update_user_profile(user)

    await update.message.reply_text(
        "Записано, жди понедельника! Можно вызвать меню, чтобы отредактировать профиль, поставить на паузу или оставить отзыв"
    )
