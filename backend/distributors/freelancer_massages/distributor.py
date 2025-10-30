import asyncio
from html import escape
from loader import bot
from aiogram.exceptions import TelegramForbiddenError

from bot.keyboards.contract_keyboard import contract_customer_keyboard
from bot.services.user_services import UserServices
from db.crud import CommonCRUDOperations as crud

async def send_new_message(task, session):
        contract = crud.get_contract_by_task_id(session=session, task_id=task.id)
        try:
            await bot.send_message(
                task.author.telegram_id,
                f"<b>Задача выполнена</b>.\n\n"
                f"<b>Название задачи</b>:  {escape(contract.task.title)}\n\n"
                f"<b>Описание задачи</b>:  {escape(contract.task.description) if contract.task.description else ''}\n\n"
                f"Исполнитель: {contract.freelancer.full_name} @{contract.freelancer.username}\n"
                f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n\n"
                f"Согласованная сумма договора: {contract.budget} руб.\n",
                reply_markup=contract_customer_keyboard(contract),
            )
        except TelegramForbiddenError:
            await UserServices.handle_user_blocked_bot(session, task.author.id)
        await asyncio.sleep(1)
        session.close()