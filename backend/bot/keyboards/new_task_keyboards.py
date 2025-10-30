from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def new_task(task, subscription):
    """
    Создает клавиатуру для уведомления о новом заказе
    :param task: Задача, о которой отправляется уведомление
    :param subscription: Подписка, на которую отправляется уведомление о заказе
    :return: Клавиатура для уведомления о новом заказе
    """
    callback_data_offer = f'lite_make_offer:{task.id}' if task.is_lite_offer else f'make_offer:{task.id}'

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Откликнуться', callback_data=callback_data_offer)],
            [InlineKeyboardButton(text='Не уведомлять от этого заказчика',
                                  callback_data=f'turn_off_not:{task.author_id}')],
            [InlineKeyboardButton(text='Заблокировать этого заказчика',
                                  callback_data=f'block_user:{task.author_id}')],
            [InlineKeyboardButton(text='Отключить подписку', callback_data=f'turn_off_sub:{subscription.id}')],
            [InlineKeyboardButton(text='Это спам', callback_data=f'spam_task:{task.id}')],
        ]
    )