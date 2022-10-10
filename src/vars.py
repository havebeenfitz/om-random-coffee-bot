import os

PROD = os.getenv('PROD', False) == 'True'

TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')
TELEGRAM_API_DEBUG_KEY = os.getenv('TELEGRAM_API_DEBUG_KEY')

POST_MESSAGES_CHAT_ID = os.getenv('POST_MESSAGES_CHAT_ID')
MEMBERSHIP_CHAT_ID = os.getenv('MEMBERSHIP_CHAT_ID')
FEEDBACK_CHAT_ID = os.getenv('FEEDBACK_CHAT_ID')
ADMIN_ACCOUNTS = os.getenv('ADMIN_ACCOUNTS').split(sep=' ')
PAIRS_PIC_URL = os.getenv('PAIRS_PIC_URL')

GEONAMES_ACCOUNT = os.getenv('GEONAMES_ACCOUNT')