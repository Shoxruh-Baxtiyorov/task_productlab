import asyncio

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from sqlalchemy.orm import Session
from babel.dates import format_date

from bot.keyboards.unban_keyboards import myblocks_unban_contract_keyboard
from bot.states.unban_states import UnbanState
from bot.states.contract_states import ContractStates
from loader import bot
from db.crud import CommonCRUDOperations as crud


r = Router()


@r.callback_query(F.data.startswith("unban_event:"), UnbanState.unban_or_not)
async def unban_contract_router(call: types.CallbackQuery, db_session: Session, state: FSMContext):
    """_summary_
    Коллбек хендлер разблокировки исполнителя
    Args:
        call (types.CallbackQuery): callback data
    """
    status = call.data.split(":")[2]
    contract_id = call.data.split(":")[1]
    if status == "unban":
        crud.unban_user_by_id(db_session, user_id=int(contract_id))
        result = crud.get_user_by_id(session=db_session, user_id=int(contract_id))
        await call.message.answer(f'Пользователь {result.full_name} @{result.username} '
                                  'был успешно разблокирован')
    try:
        state_data = await state.get_data()
        await bot.delete_message(chat_id=call.from_user.id, 
                                 message_id=state_data.get("msg_id")
                                )
    except TelegramBadRequest:
        print(f"The message was not successfully deleted")
    await call.message.answer('Оцените работу от 0 до 10')
    await state.set_state(ContractStates.work_evaluate)


@r.callback_query(F.data.startswith("myblocks_unban_event:"))
async def myblocks_unban_contract_router(call: types.CallbackQuery, db_session: Session):
    """_summary_
    Коллбек хендлер разблокировки пользователя
    Args:
        call (types.CallbackQuery): _description_
        db_session (Session): _description_
    """
    contract_id = call.data.split(":")[1]
    crud.unban_user_by_id(db_session, user_id=int(contract_id))
    try:
        await bot.edit_message_reply_markup(chat_id=call.from_user.id, 
                                 message_id=call.message.message_id, 
                                 reply_markup=None
                                )
    except TelegramBadRequest:
        print(f"The message was not successfully deleted")
    await call.message.answer('Пользователь был успешно разблокирован')


@r.message(Command("myblocks"))
async def myblocks_handler(msg: types.Message, db_session: Session):
    """
    Хендлер вывода заблокированных исполнителей с которыми работал заказчик
    """
    try:
        result = tuple(crud.get_banned_users_by_customer(session=db_session, customer_id=msg.from_user.id))
        if result:
            for i_contract in result:
                natural_date = format_date(i_contract[4], 
                                       locale="ru_RU", 
                                       format="long"
                                      )
                await msg.answer(text=f"<b>Имя:</b> {i_contract[2]}\n"
                                  f"<b>Никнейм:</b> @{i_contract[1]}\n"
                                  f"<b>Сделал задач для вас:</b> {i_contract[3]}\n"
                                  f"<b>Заблокирован до:</b> {natural_date}\n",
                             reply_markup=myblocks_unban_contract_keyboard(i_contract[0])
                             )
                await asyncio.sleep(1)
        else:
            await msg.answer("Среди исполнителей, с которыми вы работали, нет заблокированных.")
    except Exception as e:
        print(f"Ошибка при получении списка заблокированных пользователей: {e}")
        await msg.answer("Произошла ошибка при получении списка заблокированных исполнителей. Пожалуйста, попробуйте позже.")
