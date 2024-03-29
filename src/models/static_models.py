from collections import namedtuple


class Command:
    start = 'start'
    menu = 'menu'
    generate_pairs = 'generate'
    cancel = 'cancel'


class MenuCallback:
    fill_profile = 'fill_profile'
    pause = 'pause'
    send_feedback = 'send_feedback'
    generate_pairs = 'generate_pairs'
    send_message = 'send_message'

class FillProfileCallback:
    gender = 1
    meeting_format = 2
    city = 3
    bio = 4


class FeedbackCallback:
    send = 1

class SendMessageCallback:
    send_admin_message = 1

class RemoveProfileCallback:
    confirm = 'confirm_remove_profile'
    cancel = 'cancel_remove_profile'
    remove = 'remove_profile'


class GenderCallback:
    GenderType = namedtuple('GenderType', ['text', 'id'])

    male = GenderType(text="Муж", id='m')
    female = GenderType(text="Дама", id='f')
    other = GenderType(text="Сложнее", id='o')


class MeetingFormatCallback:
    MeetingFormat = namedtuple('MeetingFormat', ['text', 'id'])

    online = MeetingFormat(text='Онлайн', id='online')
    offline = MeetingFormat(text='Офлайн', id='offline')


