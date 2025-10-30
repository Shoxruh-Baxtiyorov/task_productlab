from aiogram.fsm.state import State, StatesGroup


class MakeOfferState(StatesGroup):
    description = State()
    budget = State()
    deadline = State()


class ApplyOfferState(StatesGroup):
    budget = State()