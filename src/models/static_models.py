from collections import namedtuple
from dataclasses import dataclass


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


class FillProfileCallback:
    gender = 1
    meeting_format = 2
    city = 3
    bio = 4


class FeedbackCallback:
    send = 1


class GenderCallback:
    GenderType = namedtuple('GenderType', ['text', 'id'])

    male = GenderType(text="Муж", id='m')
    female = GenderType(text="Дама", id='f')
    other = GenderType(text="Сложнее", id='o')


class MeetingFormatCallback:
    MeetingFormat = namedtuple('MeetingFormat', ['text', 'id'])

    online = MeetingFormat(text='Онлайн', id='online')
    offline = MeetingFormat(text='Офлайн', id='offline')


