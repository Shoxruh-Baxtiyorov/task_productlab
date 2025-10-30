from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def contract_executor_keyboard(contract) -> InlineKeyboardMarkup:
    """
    Клавиатура исполнителя
    :param contract: Сам контракт для получения id, или других полей.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Сдать задачу', callback_data=f'executor_contract_event:{contract.id}:pass')],
            [InlineKeyboardButton(text='Отказаться от задачи', callback_data=f'executor_contract_event:{contract.id}:cancel')],
            [InlineKeyboardButton(text='Добавить комментарий', callback_data=f'executor_contract_event:{contract.id}:comment')],
        ]
    )

def contract_customer_keyboard(contract) -> InlineKeyboardMarkup:
    """
    Клавиатура заказчика
    :param contract: Сам контракт для получения id, или других полей.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Принять задачу', callback_data=f'customer_contract_event:{contract.id}:accept')],
            [InlineKeyboardButton(text='Вернуть задачу', callback_data=f'customer_contract_event:{contract.id}:return')],
            [InlineKeyboardButton(text='Начислить баллы лояльности', callback_data=f'customer_contract_event:{contract.id}:loyalty')]
        ]
    )
    

def contract_customer_comment_keyboard(contract) -> InlineKeyboardMarkup:
    """
    Клавиатура заказчика для комментариев
    :param contract: Сам контракт для получения id, или других полей.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Написать комментарий', callback_data=f'customer_contract_event:{contract.id}:comment')],
            [InlineKeyboardButton(text='Вернуть без комментариев', callback_data=f'customer_contract_event:{contract.id}:no_comment')]
        ]
    )