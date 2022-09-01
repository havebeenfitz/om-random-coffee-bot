from collections import namedtuple


class Command:
    start = 'start'
    cancel = 'cancel'


class SurveyState:
    gender = 1
    meeting_format = 2
    city = 3
    bio = 4


class Gender:
    GenderType = namedtuple('GenderType', ['text', 'id'])

    male = GenderType(text="Муж", id='m')
    female = GenderType(text="Дама", id='f')
    other = GenderType(text="Сложнее", id='o')


class MeetingFormat:
    online = 'Онлайн'
    offline = 'Оффлайн'


