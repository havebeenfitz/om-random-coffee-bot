import logging

from src.vars import MEMBERSHIP_CHAT_ID, GEONAMES_ACCOUNT, ADMIN_ACCOUNTS
from src.models import SurveyState, Gender, MeetingFormat, Command
from src.db_helper import DBHelper
from src.handlers.pair_handlers import *

from geopy import GeoNames, Location
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from telegram.constants import ChatAction
from telegram import (
    error,
    ChatMemberBanned,
    ChatMemberLeft,
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
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        logging.info('Getting chat member..')
        member = await context.bot.get_chat_member(chat_id=MEMBERSHIP_CHAT_ID, user_id=update.effective_user.id)
        logging.info('Done..')

        if str(member.user.id) in ADMIN_ACCOUNTS:
            logging.info(f'{member.user.id} is admin. adding generate pairs handler...')
            generate_pairs_handler = CommandHandler(Command.generate_pairs, generate_pairs)
            context.application.add_handler(generate_pairs_handler)
            logging.info('Done')

        if member.status is not (ChatMemberLeft or ChatMemberBanned):
            logging.info('Member is fine, show keyboard..')
            reply_keyboard_markup = [
                [
                    InlineKeyboardButton(text=Gender.male.text, callback_data=Gender.male.id),
                    InlineKeyboardButton(text=Gender.female.text, callback_data=Gender.female.id)
                ],
                [
                    InlineKeyboardButton(text=Gender.other.text, callback_data=Gender.other.id)
                ]
            ]

            await update.message.reply_text(
                "Алоха! Расскажи немного о себе, и я подберу человека из стаи.\n\n"
                "Кто ты?",
                reply_markup=InlineKeyboardMarkup(
                    reply_keyboard_markup
                ),
            )

            logging.info('Keyboard shown')

            return SurveyState.gender
        else:
            logging.info('Sending membership message request...')
            await send_membership_message(update, context)
            logging.info('Done')
            return ConversationHandler.END
    except error.BadRequest:
        logging.info('bad request')
        await send_membership_message(update, context)
        return ConversationHandler.END


async def send_membership_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        text='Надо быть в стае, чтобы пользоваться ботом. Сходи сюда и подпишись: https://boosty.to/m0rtymerr'
    )

    return ConversationHandler.END


async def gender_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> SurveyState:
    query = update.callback_query
    await query.answer()

    context.user_data['gender'] = query.data

    logging.info("Gender of %s: %s", update.effective_user.username, update.callback_query.data)

    reply_keyboard = [
        [
            InlineKeyboardButton(MeetingFormat.online.text, callback_data=MeetingFormat.online.id),
            InlineKeyboardButton(MeetingFormat.offline.text, callback_data=MeetingFormat.offline.id)
        ]
    ]
    markup = InlineKeyboardMarkup(reply_keyboard)

    await query.edit_message_text(
        "Ок, Хочешь поболтать онлайн или в офлайне?",
        reply_markup=markup,
    )

    return SurveyState.meeting_format


async def meeting_format_handler(update: Update, context: CallbackContext) -> SurveyState:
    query = update.callback_query
    await query.answer()

    context.user_data['meeting_format'] = query.data

    logging.info("Meeting format: %s", update.callback_query.data)

    if query.data == MeetingFormat.offline.id:
        new_keyboard = [[KeyboardButton(text='Поделиться локацией', request_location=True)]]
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text='Где ты находишься? В локации будут использованы только страна и город',
            reply_markup=ReplyKeyboardMarkup(new_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return SurveyState.city
    else:
        await query.edit_message_text(
            text="Коротко напиши о своих интересах",
        )
        return SurveyState.bio


async def city_handler(update: Update, context: CallbackContext) -> SurveyState:
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

    return SurveyState.bio


async def bio_handler(update: Update, context: CallbackContext) -> int:
    bio = update.message.text
    context.user_data['bio'] = bio

    logging.info(f"Bio: {bio}")

    await update_user_in_db(update, context)

    return ConversationHandler.END


async def update_user_in_db(update, context):
    country, city = (None, None)
    user_id = update.effective_user.id
    username = update.effective_user.username
    gender = context.user_data['gender']
    meeting_format = context.user_data['meeting_format']
    bio = context.user_data['bio']

    try:
        country = context.user_data['country']
        city = context.user_data['city']

        await update.message.reply_text(
            f"Нойс, @{username}, ты заполнил анкeту!\nХочешь встретиться оффлайн в {city}\nТвои интересы: {bio}"
        )
    except None:
        await update.message.reply_text(
            f"Нойс, @{username}, ты заполнил анкeту!\nХочешь поболтать онлайн\nТвои интересы: {bio}"
        )

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    db_helper.update_user(
        user_id=str(user_id),
        username=update.effective_user.username,
        gender=gender,
        meeting_format=meeting_format,
        country=country,
        city=city,
        bio=bio
    )

    await update.message.reply_text(
        "Ты записан, жди понедельника"
    )
