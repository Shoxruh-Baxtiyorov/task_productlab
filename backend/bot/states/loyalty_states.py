from aiogram.fsm.state import State, StatesGroup

class LoyaltyStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_lifespan = State()
    waiting_for_notifications = State() 