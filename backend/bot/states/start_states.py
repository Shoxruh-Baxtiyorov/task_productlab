from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    """
    Состояние для первичного запуска бота

    Attributes:
        phone (State): ожидание номера телефона
        role (State): ожидание выбора ролей
        country (State): ожидание выбора страны
        juridical_type (State): ожидание выбор юр. статуса
        payment_types (State): ожидание выбора типов оплат
        prof_level (State): ожидание выбора проф. уровня
        skills (State): ожидание списка навыков
        bio (State): ожидания описания о себе
        notifications (State): ожидание выбора типов уведомлений
    """
    phone = State()
    role = State()
    country = State()
    juridical_type = State()
    payment_types = State()
    prof_level = State()
    skills = State()
    bio = State()
    notifications = State()