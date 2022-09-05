# import telegram.bot
# from telegram.ext import messagequeue as mq
#
#
# class RLBot(telegram.bot.Bot):
#     def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
#         super(RLBot, self).__init__(*args, **kwargs)
#         # below 2 attributes should be provided for decorator usage
#         self._is_messages_queued_default = is_queued_def
#         self._msg_queue = mqueue or mq.MessageQueue()
#
#     def __del__(self):
#         try:
#             self._msg_queue.stop()
#         except:
#             pass
#
#     @mq.queuedmessage
#     def send_message(self, *args, **kwargs):
#         return super(RLBot, self).send_message(*args, **kwargs)
#
#     @mq.queuedmessage
#     def send_photo(self, *args, **kwargs):
#         return super(RLBot, self).send_photo(*args, **kwargs)
