from aiogram.fsm.state import State, StatesGroup


class UnbanState(StatesGroup):
    unban_or_not = State()