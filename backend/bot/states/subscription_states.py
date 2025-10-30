from aiogram.fsm.state import State, StatesGroup


class SubscriptionState(StatesGroup):
    """
    Состояния для формы создания подписки
    Attributes:
        tags (State): теги подписки
        subscription_type (State): тип подписки (И, ИЛИ)
    """
    tags = State()
    budget = State()
    subscription_type = State()
