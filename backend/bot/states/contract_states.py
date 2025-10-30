from aiogram.fsm.state import State, StatesGroup

class ContractStates(StatesGroup):
    contract_return_comment = State()
    work_evaluate = State()


class ContractComment(StatesGroup):
    comment = State()