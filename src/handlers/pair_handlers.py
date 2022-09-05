import logging
import random

from collections import defaultdict
from src.db_helper import DBHelper
from src.vars import MEMBERSHIP_CHAT_ID

from telegram import Update, Bot
from telegram.ext import CallbackContext

# Logger setup
logging.getLogger().setLevel('INFO')

db_helper = DBHelper()


def generate_pairs(update: Update, context: CallbackContext):
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
        users_count = len(users)
        shuffled_users = random.sample(users, users_count)

        group_pairs = [[i, j] for i, j in zip(shuffled_users[::2], shuffled_users[1::2])]
        pairs.extend(group_pairs)

        if users_count % 2 != 0:
            no_pair_users.append(shuffled_users[users_count - 1])

    for pair in pairs:
        meeting_format = "поболтать онлайн" if pair[0]['format'] == 'online' else f"встретиться в {pair[0]['city']}"

        context.bot.send_message(
            chat_id=pair[0]['id'],
            # chat_id=update.effective_user.id,
            text=f"Штош, @{pair[0]['username']}!\n\n"\
            f"Твоя пара на эту неделю @{pair[1]['username']}. "\
            f"Вы хотели {meeting_format}.\n\n"\
            f"Можно начать разговор с обсуждения интересов собеседника: {pair[1]['bio']}"
        )

        context.bot.send_message(
            chat_id=pair[1]['id'],
            # chat_id=update.effective_user.id,
            text=f"Штош, @{pair[1]['username']}!\n\n"\
            f"Твоя пара на эту неделю @{pair[0]['username']}. "\
            f"Вы хотели {meeting_format}.\n\n"\
            f"Можно начать разговор с обсуждения интересов собеседника: {pair[0]['bio']}"
        )

        # pic = None
        #
        # try:
        #     pic = open('./sobaka.jpg', 'r+b')
        #
        #     context.bot.send_document(
        #         # chat_id=pair[0]['id'],
        #         chat_id=update.effective_user.id,
        #         document=pic
        #     )
        #
        #     context.bot.send_document(
        #         # chat_id=pair[1]['id'],
        #         chat_id=update.effective_user.id,
        #         document=pic
        #     )
        #
        # finally:
        #     pic.close()

        logging.info(f"{pair[0]['username']}, your pair is {pair[1]['username']}")
        logging.info(f"{pair[1]['username']}, your pair is {pair[0]['username']}")

    for no_pair_user in no_pair_users:
        context.bot.send_message(
            chat_id=MEMBERSHIP_CHAT_ID,
            # chat_id=update.effective_user.id,
            text=f"Сорян, @{no_pair_user['username']}!\n"\
            "В этот раз пары не нашлось из-за разных форматов встреч / городов / количества участников\n\n"\
            "Исправимся на следующей неделе, но это не точно"
        )
        logging.info(f"{no_pair_user['username']}, 'no pair for you, dayymn. Meeting format doesn\'t match")

    logging.info('Generating pairs done!')
