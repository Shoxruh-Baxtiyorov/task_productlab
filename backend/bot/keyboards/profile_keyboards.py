from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def settings_keyboard():
    """
    Создание клавиатуры для перезаполнения профиля
    :return: клавиатура с кнопкой перезаполнения
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Заполнить заново', callback_data='restart_register')]
        ]
    )


def push_keyboard():
    """
    Создает клавиатуру для меню настройки оповещений
    :return: клавиатура для меню оповещений
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Мои подписки', callback_data='my_subs')]
        ]
    )
