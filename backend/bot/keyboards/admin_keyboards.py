from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from db.models import *


def distribution_choose_role(chosen_roles):
    """
    Клавиатура для выбора ролей для рассылки
    :param chosen_roles: уже выбранные роли
    :return: клавиатура выбора ролей для рассылки
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Исполнители' if RoleType['FREELANCER'] not in chosen_roles else "☑️Исполнители",
                callback_data='FREELANCER'
            )],
            [InlineKeyboardButton(
                text='Заказчики' if RoleType['CLIENT'] not in chosen_roles else '☑️Заказчики',
                callback_data='CLIENT'
            )],
            [InlineKeyboardButton(
                text='Далее➡️',
                callback_data='next'
            )]
        ]
    )


def confirm():
    """
    Клавиатура для подтверждения рассылки или чего либо еще
    :return: клавиатура для подтверждения
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Подтвердить', callback_data='confirm')],
            [InlineKeyboardButton(text='Отменить', callback_data='cancel')]
        ]
    )


def user_sorting_options():
    """
    Клавиатура для выбора способа сортировки пользователей
    :return: клавиатура с вариантами сортировки
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="По дате", callback_data='sort_by__date')],
            [InlineKeyboardButton(text="По количеству задач", callback_data='sort_by__tasks')]
        ]
    )
