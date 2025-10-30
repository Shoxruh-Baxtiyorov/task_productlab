from aiogram.fsm.state import State, StatesGroup


class MassiveMessagingState(StatesGroup):
    roles = State()
    message = State()
    confirm = State()
