import re


def str_to_hours_converter(message: str) -> int:
    """Конвертируем сообщение пользователя в часы"""
    message = message.lower()
    message = message.split(' ')
    hours_sum = 0
    for data in message:
        if 'д' in data:
            hours_sum = hours_sum + int(data.replace('д', ''))*24
        elif 'ч' in data:
            hours_sum = hours_sum + int(data.replace('ч', ''))

    return hours_sum


def deadline_message_validate(msg: str) -> str | None:
    """Проверяем введенное время"""
    msg = msg.lower()
    pattern = re.compile(r'''
        ^\s*
        (
            \d+д\s+\d+ч     # дни + пробел + часы
            |
            \d+ч\s+\d+д     # часы + пробел + дни
            |
            \d+д            # только дни
            |
            \d+ч            # только часы
        )
        \s*$
    ''', re.VERBOSE | re.IGNORECASE)

    if not msg or msg.strip() == '':
        return None
    if not pattern.fullmatch(msg):
        return None
    if re.search(r'\d+\s*д', msg) or re.search(r'\d+\s*ч', msg):
        return msg
    return None


def deadline_converted_output(hours: int) -> str:
    """Переводим общее количество часов в формат 'дни часы'"""
    try:
        return f"{hours//24}д {hours%24}ч"
    except TypeError:
        return f"0д 0ч"