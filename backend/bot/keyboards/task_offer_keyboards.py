from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def task_offer_keyboard_for_author(offer):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🎯 Выбрать исполнителя', callback_data=f'apply_offer:{offer.id}:apply')],
            [InlineKeyboardButton(text='✅ Подписать договор', callback_data=f'finish_apply_offer:{offer.id}:fast')],
            [InlineKeyboardButton(text='❌ Отклонить исполнителя', callback_data=f'apply_offer:{offer.id}:cancel')]
        ]
    )


def task_offer_apply(offer):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Подписать договор', callback_data=f'finish_apply_offer:{offer.id}:apply')],
            [InlineKeyboardButton(text='Отклонить оффер', callback_data=f'finish_apply_offer:{offer.id}:cancel')]
        ]
    )


def task_offer_keyboard_for_freelancer(offer):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='✅ Подписать договор', callback_data=f'finish_apply_offer:{offer.id}:fast')],
            [InlineKeyboardButton(text='❌ Сбросить отклик', callback_data=f'apply_offer:{offer.id}:cancel')]
        ]
    )


def task_offer_return(task):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Вернуть задачу в облако", callback_data=f"return_task:{task.id}")]
        ]
    )