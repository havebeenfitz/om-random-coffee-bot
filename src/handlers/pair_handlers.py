import logging
import random

from collections import defaultdict
from src.db_helper import DBHelper
from src.vars import MEMBERSHIP_CHAT_ID, PAIRS_PIC_URL

from telegram import Update, Bot
from telegram.ext import CallbackContext

# Logger setup
logging.getLogger().setLevel('INFO')

db_helper = DBHelper()


async def generate_pairs(update: Update, context: CallbackContext):
    logging.info('Generating pairs...')

    pairs: list[list] = []
    no_pair_users: list = []
    users = db_helper.get_all_users()
    grouped_users_dict = defaultdict(list)

    for user in users:
        if user['city']:
            grouped_users_dict[user['city']].append(user)
        else:
            grouped_users_dict[user['format']].append(user)

    for group, users in grouped_users_dict.items():
        _shuffle_pairs(no_pair_users, pairs, users)

    for pair in pairs:
        await _send_pair_messages(update, context, pair)

    for no_pair_user in no_pair_users:
        await _send_no_pair_messages(update, context, no_pair_user)

    logging.info('Generating pairs done!')


# Private

def _shuffle_pairs(no_pair_users, pairs, users):
    users_count = len(users)
    shuffled_users = random.sample(users, users_count)
    group_pairs = [[i, j] for i, j in zip(shuffled_users[::2], shuffled_users[1::2])]
    pairs.extend(group_pairs)

    if users_count % 2 != 0:
        no_pair_users.append(shuffled_users[users_count - 1])


async def _send_pair_messages(update, context, pair):
    meeting_format = "поболтать онлайн" if pair[0]['format'] == 'online' else f"встретиться офлайн. Локация: {pair[0]['city']}"
    first_user_id = int(pair[0]['id'])
    second_user_id = int(pair[1]['id'])
    first_user_name = pair[0]['username']
    second_user_name = pair[1]['username']
    first_user_bio = pair[0]['bio']
    second_user_bio = pair[1]['bio']

    await context.bot.send_message(
        chat_id=first_user_id,
        # chat_id=update.effective_user.id,
        text=f"Штош, @{first_user_name}!\n\n" \
             f"Твоя пара на эту неделю @{second_user_name}. " \
             f"Вы оба хотели {meeting_format}.\n\n" \
             f"Можно начать разговор с обсуждения интересов собеседника: {second_user_bio}"
    )
    await context.bot.send_photo(
        chat_id=first_user_id,
        # chat_id=update.effective_user.id,
        photo=PAIRS_PIC_URL
    )

    await context.bot.send_message(
        chat_id=second_user_id,
        # chat_id=update.effective_user.id,
        text=f"Штош, @{second_user_name}!\n\n" \
             f"Твоя пара на эту неделю @{first_user_name}. " \
             f"Вы хотели {meeting_format}.\n\n" \
             f"Можно начать разговор с обсуждения интересов собеседника: {first_user_bio}"
    )
    await context.bot.send_photo(
        chat_id=second_user_id,
        # chat_id=update.effective_user.id,
        photo=PAIRS_PIC_URL
    )

    logging.info(f"{first_user_name}, paired with {second_user_name}")


async def _send_no_pair_messages(update, context, no_pair_user):
    await context.bot.send_message(
        chat_id=MEMBERSHIP_CHAT_ID,
        # chat_id=update.effective_user.id,
        text=f"Сорян, @{no_pair_user['username']}!\n" \
             "В этот раз пары не нашлось из-за разных форматов встреч / городов / количества участников\n\n" \
             "Исправимся на следующей неделе, но это не точно"
    )
    logging.info(f"{no_pair_user['username']}, 'no pair for you, dayymn. Meeting format doesn\'t match")