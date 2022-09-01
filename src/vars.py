import os

TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')
TELEGRAM_API_DEBUG_KEY = os.getenv('TELEGRAM_API_DEBUG_KEY')

MEMBERSHIP_CHAT_ID = os.getenv('MEMBERSHIP_CHAT_ID')
PROD = os.getenv('PROD', False) == 'True'
