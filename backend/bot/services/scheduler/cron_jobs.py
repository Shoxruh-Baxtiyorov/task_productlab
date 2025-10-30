
monthly_rating_bonus = {
    "func": "monthly_rating_bonus",
    "trigger": "cron",
    "day": "1",
    "hour": "08",
    "minute": "00",
    "timezone": "Europe/Moscow",
}

segment_update = {
    "func": "parse_segments",
    "trigger": "interval",
    "minutes": 5,
    "timezone": "Europe/Moscow",
}

hourly_not_registered_users = {
    'func': "hourly_not_registered_users",
    'trigger': 'interval',
    'minutes': 5,
}