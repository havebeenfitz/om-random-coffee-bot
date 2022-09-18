from dataclasses import dataclass
from collections import namedtuple


@dataclass
class Gender:
    GenderType = namedtuple('GenderType', ['text', 'id'])

    male = GenderType(text="Муж", id='m')
    female = GenderType(text="Дама", id='f')
    other = GenderType(text="Сложнее", id='o')


@dataclass
class MeetingFormat:
    MeetingFormat = namedtuple('MeetingFormat', ['text', 'id'])

    online = MeetingFormat(text='Онлайн', id='online')
    offline = MeetingFormat(text='Офлайн', id='offline')


@dataclass
class User:
    def __init__(self, user_dict: dict):
        self.user_id = user_dict['user_id']
        self.username = user_dict['username']
        self.is_paused = user_dict['is_paused']
        self.gender = user_dict['gender']
        self.meeting_format = user_dict['format']
        self.bio = user_dict['bio']

        if ('city' and 'country') in user_dict:
            self.city = user_dict['city']
            self.country = user_dict['country']