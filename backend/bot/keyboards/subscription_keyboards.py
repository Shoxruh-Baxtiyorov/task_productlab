from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from db.models import SubscriptionStatusType


def my_subscription_view(subscription):
    """
    Создает клавиатуру для меню отдельной подписки
    :param subscription: подписка
    :return: Клавиатура для меню отдельной подписки
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отключить подписку'
            if subscription.status == SubscriptionStatusType.SEND else
            'Включить подписку', callback_data=f'sub_on_off:{subscription.id}')],
            [InlineKeyboardButton(text='Удалить подписку', callback_data=f'sub_del:{subscription.id}')],
            [InlineKeyboardButton(text='⬅️Назад в список', callback_data='my_subs')]
        ]
    )


def my_subscriptions_list(subscriptions):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='➕Добавить подписку', callback_data='add_sub')],
            [InlineKeyboardButton(text='⬅️Назад', callback_data='push_menu')]
        ] + [[InlineKeyboardButton(text=','.join(sub.tags), callback_data=f'view_sub:{sub.id}')] for sub in subscriptions]
    )


def choose_budget():
    """
    Создает клавиатуру для выбора бюджета задачи.
    :return: Клавиатура с вариантами бюджета
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='0₽ - 1000₽', callback_data='0-1000'),
             InlineKeyboardButton(text='1000₽ - 10000₽', callback_data='1000-10000')],
            [InlineKeyboardButton(text='10000₽ - 100000₽', callback_data='10000-100000'),
             InlineKeyboardButton(text='Любой', callback_data='none')]
        ]
    )


def choose_subcription_type():
    """
    Создает клавиатуру для выбора типа подписки
    :return: Клавиатура с вариантами для типа подписки
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='И', callback_data='AND')],
            [InlineKeyboardButton(text='ИЛИ', callback_data='OR')]
        ]
    )
