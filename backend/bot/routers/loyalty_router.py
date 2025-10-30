from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from bot.states.loyalty_states import LoyaltyStates
from db.crud import CommonCRUDOperations as crud
from bot.services.services_manager import service_manager

r = Router(name='loyalty_router')
scheduler_services = service_manager.get_scheduler_services()

@r.callback_query(F.data.startswith('loyalty_points:'))
async def handle_loyalty_points(callback: types.CallbackQuery, state: FSMContext, db_session: Session):
    """Handle loyalty points award initiation"""
    contract_id = int(callback.data.split(':')[1])
    contract = crud.get_contract_by_id(db_session, contract_id)
    
    await state.set_state(LoyaltyStates.waiting_for_amount)
    await state.update_data(contract_id=contract_id)
    
    await callback.message.edit_text(
        "Пожалуйста, пришлите сумму баллов, которую нужно начислить на счет исполнителя."
    )

@r.message(LoyaltyStates.waiting_for_amount)
async def handle_points_amount(message: types.Message, state: FSMContext, db_session: Session):
    """Handle points amount input"""
    try:
        amount = int(message.text)
        data = await state.get_data()
        contract = crud.get_contract_by_id(db_session, data['contract_id'])

        expires_at = datetime.now() + timedelta(days=1)
        points = crud.create_loyalty_points(
            session=db_session,
            user_id=contract.freelancer_id,
            amount=amount,
            expires_at=expires_at,
            notification_count=3 
        )
        
        await message.answer(
            f"Готово, вы успешно начислили {amount} баллов исполнителю.\n"
            f"Срок действия баллов: 1 день."
        )

        await message.bot.send_message(
            contract.freelancer.telegram_id,
            f"Вам начислено {amount} баллов лояльности!\n"
            f"Срок действия баллов: 1 день.\n"
            f"Баллы будут автоматически использованы в следующей задаче."
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число баллов.")

@r.callback_query(F.data == "skip_loyalty_points")
async def skip_loyalty_points(callback: types.CallbackQuery):
    """Handle skipping loyalty points award"""
    await callback.message.edit_text(
        "Начисление баллов пропущено.",
        reply_markup=None
    )
    await callback.answer() 