from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from db.models import RoleType, PaymentType, NotificationType


def open_task(task):
    """
    Создает клавиатуру для открытого по ссылке заказа
    :param task: заказ
    :return: клавиатура заказа
    """
    callback_data_offer = f'lite_make_offer:{task.id}' if task.is_lite_offer else f'make_offer:{task.id}'
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Откликнуться', callback_data=callback_data_offer)],
            [InlineKeyboardButton(text='Не уведомлять от этого заказчика',
                                  callback_data=f'turn_off_not:{task.author_id}')],
            [InlineKeyboardButton(text='Заблокировать этого заказчика',
                                  callback_data=f'block_user:{task.author_id}')],
            [InlineKeyboardButton(text='Это спам', callback_data=f'spam_task:{task.id}')],
        ]
    )


def send_phone_number_keyboard():
    """
    Создание клавиатуры для отправки номера

    :return: клавиатура для отправки номера
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Отправить номер', request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def send_location_keyboard():
    """
    Создание клавиатуры для отправки геолокации

    :return: Клавиатура для отправки геолокации
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Отправить локацию', request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def choose_role_keyboard(chosen_roles):
    """
    Создание клавиатуры для выбора ролей

    :param chosen_roles: список уже выбранных ролей пользователем
    :return: Клавиатура для выбора ролей
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Я исполнитель' if RoleType['FREELANCER'] not in chosen_roles else "☑️Я исполнитель", callback_data='FREELANCER')],
            [InlineKeyboardButton(text='Я заказчик' if RoleType['CLIENT'] not in chosen_roles else '☑️Я заказчик', callback_data='CLIENT')],
            [InlineKeyboardButton(text='Далее➡️', callback_data='next')]
        ]
    )


def choose_country():
    """
    Создание клавиатуры для выбора страны

    :return: Клавиатура для выбора страны
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Я из России', callback_data='RUSSIA')],
            [InlineKeyboardButton(text='Я не из России', callback_data='NOTRUSSIA')]
        ]
    )


def choose_juridical_type():
    """
    Создание клавиатуры для выбора юр. статуса

    :return: Клавиатура для выбора юр. статуса
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='ИП', callback_data='IP')],
            [InlineKeyboardButton(text='Самозанятый', callback_data='SELF_EMPLOYED')],
            [InlineKeyboardButton(text='ООО', callback_data='OOO')],
            [InlineKeyboardButton(text='Физлицо', callback_data='PHYSICAL')],
        ]
    )


def choose_payment_types(chosen_payments):
    """
    Создание клавиатуры для выбора способов оплаты

    :param chosen_payments: список уже выбранных способов оплаты пользователем
    :return: Клавиатура для выбора способов оплаты
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Сбер' if PaymentType['SBER'] not in chosen_payments else "☑️Сбер", callback_data='SBER')],
            [InlineKeyboardButton(text='Самозанятость' if PaymentType['SELF_EMPLOYED'] not in chosen_payments else '☑️Самозанятость', callback_data='SELF_EMPLOYED')],
            [InlineKeyboardButton(text='Крипта' if PaymentType['CRYPTO'] not in chosen_payments else '☑️Крипта', callback_data='CRYPTO')],
            [InlineKeyboardButton(text='Безнал' if PaymentType['NONCASH'] not in chosen_payments else '☑️Безнал', callback_data='NONCASH')],
            [InlineKeyboardButton(text='Далее➡️', callback_data='next')]
        ]
    )


def choose_prof_level():
    """
    Создание клавиатуры для выбора проф. уровня

    :return: Клавиатура для выбора проф. уровня
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Junior', callback_data='JUNIOR')],
            [InlineKeyboardButton(text='Middle', callback_data='MIDDLE')],
            [InlineKeyboardButton(text='Senior', callback_data='SENIOR')]
        ]
    )


def choose_notification_type(chosen_notifications):
    """
    Создание клавиатуры для выбора типов уведомлений

    :param chosen_notifications: список уже выбранных типов уведомлений пользователем
    :return: Клавиатура для выбора типов уведомлений
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Обновления платформы' if NotificationType['PLATFORM'] not in chosen_notifications else "☑️Обновления платформы", callback_data='PLATFORM')],
            [InlineKeyboardButton(text='Новые заказы из подписок' if NotificationType['NEWTASKS'] not in chosen_notifications else '☑️Новые заказы из подписок', callback_data='NEWTASKS')],
            [InlineKeyboardButton(text='Отклики на мои заказы' if NotificationType['RESPONSES'] not in chosen_notifications else '☑️Отклики на мои заказы', callback_data='RESPONSES')],
            [InlineKeyboardButton(text='Далее➡️', callback_data='next')]
        ]
    )
