from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def unban_contract_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для разблокировки исполнителя
    Args:
        user_id (int): ID пользователя для разблокировки
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Разблокировать", 
                    callback_data=f"unban_event:{user_id}:unban"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Пропустить", 
                    callback_data=f"unban_event:{user_id}:skip"
                )
            ]
        ]
    )

def myblocks_unban_contract_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """
    Альтернативная клавиатура для разблокировки
    Args:
        user_id (int): ID пользователя для разблокировки
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Разблокировать", 
                    callback_data=f"myblocks_unban_event:{user_id}"
                )
            ]
        ]
    )