from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def rating_bonus_button(datetime_of_message: datetime):
    return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='ПОЛУЧИТЬ БОНУС', callback_data=f'bonus_{datetime_of_message}')],

            ]
        )


def info_rating_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Информация о рейтинге', callback_data='info_rating')],
        ]
    )
