from src.db_helper import DBHelper
from telegram import Bot, ChatMember
from telegram.ext import Application, AIORateLimiter
from telegram.constants import ChatAction
from src.vars import *
import asyncio

async def clean_up():
    db = DBHelper(override_prod=True)
    users = db.get_all_users()
    application = Application.builder() \
        .token(TELEGRAM_API_KEY) \
        .rate_limiter(AIORateLimiter(overall_max_rate=25)) \
        .build()

    await application.initialize()

    print('Number of active users: ', len(users))

    for user in users:
        try:
            await application.bot.send_chat_action(chat_id=user.user_id, action=ChatAction.TYPING)
            print(user.user_id, end=' ')
            print('stayed')
            pass
        except:
            print(user.user_id, end=' ')
            print('blocked the bot')
            db.delete_user(user.user_id)

if __name__ == '__main__':
    asyncio.run(clean_up())
