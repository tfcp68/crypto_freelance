import datetime


TIME_CONSTANTS = {
    'h': "hour",
    'M': 'minute',
    'd': 'day',
    'w': "week",
    'm': "month",
}

TIME_CONSTANT_TO_MULT = {
    "M": 60,
    "h": 60 * 60,
    "d": 60 * 60 * 24,
    "w": 60 * 60 * 24 * 7,
    "m": 60 * 60 * 24 * 30
}

FEE_PERCENT = 1


class SignType:
    MAKE_DEAL = 1
    EXECUTION = 2
    JUDGMENT = 3
    ACCEPT_SOLUTION = 4
    DEFAULT = 5


MINIMAL_JUDGMENT_TIME = datetime.timedelta(minutes=1)
