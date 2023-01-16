import logging
import random

from collections import defaultdict
from src.db_helper import DBHelper
from src.vars import POST_MESSAGES_CHAT_ID, PAIRS_PIC_URL, PROD, ADMIN_ACCOUNTS
from src.models.user import User
from src.vars import TELEGRAM_API_KEY

from telegram import Update, Bot
from telegram.ext import CallbackContext, Application, AIORateLimiter
from telegram.constants import ChatAction

# Logger setup
logging.getLogger().setLevel('INFO')

db_helper = DBHelper()

async def generate_pairs(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    logging.info('Cleaning up db just in case...')
    await clean_up(update, context)

    logging.info('Sending start pairing message to membership group')
    await context.bot.send_message(
        chat_id=POST_MESSAGES_CHAT_ID if PROD else update.effective_user.id,
        text="Сегодня понедельник, стартуем казино..."
    )
    await context.bot.send_dice(
        chat_id=POST_MESSAGES_CHAT_ID if PROD else update.effective_user.id
    )

    logging.info('Generating strict pairs...')

    users: [User] = db_helper.get_all_users()
    grouped_users_dict = defaultdict(list[User])

    pairs: list[list] = []
    no_initial_pair_users: list = []

    for user in users:
        if user.meeting_format == 'offline':
            grouped_users_dict[user.city].append(user)
        else:
            grouped_users_dict[user.meeting_format].append(user)

    for group, group_users in grouped_users_dict.items():
        _shuffle_pairs(no_initial_pair_users, pairs, group_users)

    for pair in pairs:
        await _send_pair_messages(update, context, pair, is_loose_pairing=False)

    # Shuffle users without initial pairs
    if len(no_initial_pair_users) > 0:
        logging.info('Generating loose pairs...')

        no_pair_users = []
        loose_pairs: list[list] = []

        await context.bot.send_message(
            chat_id=POST_MESSAGES_CHAT_ID if PROD else update.effective_user.id,
            text="Не хватает людей по локациям, пробую сматчить всех, кто остался..."
        )

        _shuffle_pairs(no_pair_users, loose_pairs, no_initial_pair_users)

        for pair in loose_pairs:
            await _send_pair_messages(update, context, pair, is_loose_pairing=True)

        assert len(no_pair_users) <= 1

        for no_pair_user in no_pair_users:
            await _send_no_pair_messages(update, context, no_pair_user)

    logging.info('Generating pairs done!')

    await context.bot.send_message(
        chat_id=POST_MESSAGES_CHAT_ID if PROD else update.effective_user.id,
        text="Сгенерил вам пары на эту неделю, проверьте личку!\n\n"
             "P.S. Отзывы и идеи по улучшению можно оставить через меню"
    )

    await context.bot.send_message(chat_id=update.effective_user.id, text="Clean up done")


# Private

def _shuffle_pairs(no_pair_users, pairs, users):
    users_count = len(users)
    shuffled_users = random.sample(users, users_count)
    group_pairs = [[i, j] for i, j in zip(shuffled_users[::2], shuffled_users[1::2])]
    pairs.extend(group_pairs)

    if users_count % 2 != 0:
        no_pair_users.append(shuffled_users[users_count - 1])


async def _send_pair_messages(update, context, pair: (User, User), is_loose_pairing: bool):
    meeting_format = "поболтать онлайн" if pair[0].meeting_format == 'online' \
        else f"встретиться офлайн. Локация: {pair[0].city}"
    first_user_id = int(pair[0].user_id)
    second_user_id = int(pair[1].user_id)
    first_user_name: str
    second_user_name: str
    first_user_bio = pair[0].bio
    second_user_bio = pair[1].bio

    try:
        first_user_name = pair[0].username
        second_user_name = pair[1].username

        no_initial_match_text = "Не хватает людей в твоей локации, но есть вариант поболтать онлайн!\n\n"

        first_user_text = (f"Штош, @{first_user_name}!\n\n" if first_user_name else "Заполни пожалуйста ник, тебе невозможно написать.\n\n") + \
            (f"Твоя пара на эту неделю @{second_user_name}.\n\n" if second_user_name else "У твоей пары не заполнен ник, надеюсь у тебя заполнен и тебе напишут\n\n") + \
            (f"Вы хотели {meeting_format}.\n\n" if not is_loose_pairing else no_initial_match_text) + \
            f"Можно начать разговор с обсуждения интересов собеседника: {second_user_bio}"

        await context.bot.send_message(
            chat_id=first_user_id if PROD else update.effective_user.id,
            text=first_user_text
        )

        await context.bot.send_photo(
            chat_id=first_user_id if PROD else update.effective_user.id,
            photo=PAIRS_PIC_URL
        )

        second_user_text = (f"Штош, @{second_user_name}!\n\n" if second_user_name else "Заполни пожалуйста ник, тебе невозможно будет написать.\n\n") + \
            (f"Твоя пара на эту неделю @{first_user_name}.\n\n" if first_user_name else "У твоей пары не заполнен ник, надеюсь у тебя заполнен и тебе напишут\n\n") + \
            (f"Вы хотели {meeting_format}.\n\n" if not is_loose_pairing else no_initial_match_text) + \
            f"Можно начать разговор с обсуждения интересов собеседника: {first_user_bio}"

        await context.bot.send_message(
            chat_id=second_user_id if PROD else update.effective_user.id,
            text=second_user_text
        )

        await context.bot.send_photo(
            chat_id=second_user_id if PROD else update.effective_user.id,
            photo=PAIRS_PIC_URL
        )

        logging.info(f"{first_user_name}, paired with {second_user_name}")
    except TypeError as e:
        logging.info(f"error pairing users: {e}")


async def _send_no_pair_messages(update, context, no_pair_user: User):
    no_pair_text = (f"Сорян, @{no_pair_user.username}!\n" if (no_pair_user.username is not None) else "Сорян\n\n") + \
        "В этот раз пары не нашлось из-за разных форматов встреч / городов / количества участников\n\n" + \
        "Исправимся в ближайшее время, предложим пару из другого города для онлайн беседы\n\n" + \
        "Пока что можно переключиться на онлайн, отредактировав профиль"

    await context.bot.send_message(
        chat_id=no_pair_user.user_id if PROD else update.effective_user.id,
        text=no_pair_text
    )

    logging.info(f"{no_pair_user.username}, with no pair")


async def clean_up(update, context):
    users = db_helper.get_all_users()

    await context.bot.send_message(chat_id=update.effective_user.id, text=f"Number of active users: {len(users)}")

    for user in users:
        try:
            await context.bot.send_chat_action(chat_id=user.user_id, action=ChatAction.TYPING)
            logging.info(f"{user.user_id} stayed")
            pass
        except:
            logging.info(f"{user.user_id} blocked the bot, removing from db")
            db_helper.delete_user(user.user_id)

    await context.bot.send_message(chat_id=update.effective_user.id, text="Clean up done")
