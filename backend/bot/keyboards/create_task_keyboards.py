from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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
             InlineKeyboardButton(text='По договору', callback_data='none')]
        ]
    )


def confirm_task():
    """
    Создает клавиатуру для подтверждения создания задачи
    :return: Клавиатура с подтверждением создания задачи
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Подтвердить', callback_data='confirm'),
             InlineKeyboardButton(text='Отменить', callback_data='cancel')]
        ]
    )


def litetask_tags_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Добавить теги', callback_data='add_tags'),
             InlineKeyboardButton(text='Пропустить', callback_data='pass_tags')]
        ]
    )

def choose_auto_response():
    """
    Создает клавиатуру для выбора автоматического приема откликов
    :return: Клавиатура с вариантами выбора: Всех, по правилам, пропустить
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Абсолютно всех', callback_data='all'),
             InlineKeyboardButton(text='По правилам', callback_data='rules')],
            [InlineKeyboardButton(text='Пропустить', callback_data='pass')]
        ]
    )



def choose_allow_lite_offer():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Да', callback_data='yes'),
                InlineKeyboardButton(text='Нет', callback_data='no'),
                InlineKeyboardButton(text='Пропустить', callback_data='pass')
            ]
        ]
    )