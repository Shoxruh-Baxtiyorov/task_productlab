from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



def question_keyboard():

    return InlineKeyboardMarkup(inline_keyboard=[
                        [
                            InlineKeyboardButton(text="Да", callback_data="resume_question_yes"),
                            InlineKeyboardButton(text="Нет", callback_data="resume_question_no")
                        ]
                    ])


def resume_reminder_keyboard():
    """
    Клавиатура для напоминания о загрузке резюме
    """
    return InlineKeyboardMarkup(inline_keyboard=[
                        [
                            InlineKeyboardButton(text="У меня нет резюме", callback_data="no_resume")
                        ]
                    ])