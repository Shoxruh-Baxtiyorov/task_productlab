from html import escape
import pytz
from aiogram import Router, F, types
from aiogram.filters import Command
from datetime import datetime, timedelta
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from bot.keyboards.contract_keyboard import (
    contract_executor_keyboard,
    contract_customer_keyboard,
    contract_customer_comment_keyboard,
)
from bot.states.contract_states import ContractStates, ContractComment
from bot.states.unban_states import UnbanState
from db.crud import CommonCRUDOperations as crud
from db.models import User, ContractStatusType, RaitingChangeDirection, TaskStatusType
from bot.constants.rating import (
    FINISH_WORK_RATING_INCREASE,
    FINISH_WORK_RATING_INCREASE_COMMENT,
    CANCELTASK_RATING_DECREASE,
    CANCELTASK_RATING_DECREASE_COMMENT
)
from bot.services.rating_services import RatingService
from bot.services.services_manager import service_manager
from bot.keyboards.unban_keyboards import (
    unban_contract_keyboard,
    myblocks_unban_contract_keyboard,
)
from bot.utils.deadline_utils import deadline_converted_output
from bot.states.loyalty_states import LoyaltyStates

r = Router()
user_services = service_manager.get_user_services()
scheduler_services = service_manager.get_scheduler_services()


@r.message(Command("contracts"))
async def active_contract(msg: types.Message, db_session: Session, user: User):
    """
    Команда управления контрактами, пока выдает только последний активный контракт.
    """
    contracts = crud.get_contracts_by_user_id(session=db_session, user_id=user.id)
    contracts_active_flags = False

    # Текущее время в Москве
    use_tz = pytz.timezone("Europe/Moscow")
    now = datetime.now(pytz.utc).astimezone(use_tz)

    for contract in contracts:
        if contract.status == ContractStatusType.ATWORK:
            contracts_active_flags = True

            if contract.deadline_at:
                time_left = contract.deadline_at.astimezone(tz=use_tz) - now
                days_left = time_left.days
                hours_left, remain_min = divmod(time_left.seconds, 3600)
                minutes_left, seconds_left = divmod(remain_min, 60)

                time_out = ".".join(
                    [
                        f"{days_left}дн" if days_left else "",
                        f"{hours_left:02}ч" if hours_left else "",
                        f"{minutes_left:02}м" if minutes_left else "00м",
                        f"{seconds_left:02}с" if seconds_left else "00с",
                    ]
                )
            else:
                time_out = "Не установлено."

            await msg.answer(
                "\n".join(
                    [
                        f"<b>Текущая задача</b>:  {contract.task.title}\n",
                        f"<b>Описание задачи</b>:  {escape(contract.task.description) if contract.task.description else ''}\n",
                        f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n",
                        f"Согласованная сумма договора: {contract.budget} руб.\n",
                        f"Осталось: {time_out}.\n",
                        (
                            f"Комментарий исполнителя: {contract.comment_freelancer}"
                            if contract.comment_freelancer
                            else ""
                        ),
                    ]
                ),
                reply_markup=contract_executor_keyboard(contract),
            )

    if not contracts_active_flags:
        await msg.answer("Нет активных задач.")


@r.callback_query(F.data.startswith('executor_contract_event:'))
async def executor_contract_callback(cb: types.CallbackQuery, db_session: Session, user: User, state, service_manager):
    """
    Коллбэк хэндлер исполнителя, сдать контракт заказчику или отказаться от контракта.
    """
    contract_id = int(cb.data.split(":")[1])
    status = cb.data.split(":")[2]
    contract = crud.get_contract_by_id(session=db_session, contract_id=contract_id)
    task = crud.get_task_by_id(session=db_session, task_id=contract.task_id)
    await state.update_data(contract_id=contract_id)

    text_comment_freelancer = (
        f"Комментарий исполнителя: {contract.comment_freelancer}"
        if contract.comment_freelancer
        else ""
    )

    if status == "pass":
        if contract.status == ContractStatusType.INSPECTED:
            await cb.message.answer("Задача уже сдана.")
            return
        if not contract.comment_freelancer or contract.comment_freelancer == "false":
            msg = await cb.message.answer(
                "Приложите обязательный комментарий.")
            await state.set_state(ContractComment.comment)
            await state.update_data(comment_msg_to_delete=msg.message_id,
                                    contract_id=contract.id)
            await cb.message.delete()
            return
        loyalty_points = crud.get_latest_active_loyalty_points(
            db_session, contract.freelancer_id, client_id=contract.task.author_id
        )
        points_text = f" + {loyalty_points.amount} баллов" if loyalty_points else ""

        # Сначала отправляем все сообщения
        await cb.message.edit_text(
            f"<b>Задача отправлена на проверку заказчику... Ожидайте</b>\n\n"
            f"<b>Название задачи</b>:  {escape(contract.task.title)}\n\n"
            f"<b>Описание задачи</b>:  {escape(contract.task.description) if contract.task.description else ''}\n\n"
            f"Исполнитель: {contract.freelancer.full_name} @{contract.freelancer.username}\n"
            f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n\n"
            f"Согласованная сумма договора: {contract.budget} руб.{points_text}\n\n"
            f"{text_comment_freelancer}",
        )

        await service_manager.rating_services.update_rating_weekly_tasks(user.id)

        contract.status = ContractStatusType.INSPECTED
        db_session.commit()
        # Сообщение заказчику
        await cb.bot.send_message(
            contract.task.author.telegram_id,
            f"<b>Задача выполнена</b>.\n\n"
            f"<b>Название задачи</b>:  {escape(contract.task.title)}\n\n"
            f"<b>Описание задачи</b>:  {escape(contract.task.description) if contract.task.description else ''}\n\n"
            f"Исполнитель: {contract.freelancer.full_name} @{contract.freelancer.username}\n"
            f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n\n"
            f"Согласованная сумма договора: {contract.budget} руб.{points_text}\n\n"
            f"{text_comment_freelancer}",
            reply_markup=contract_customer_keyboard(contract),
        )

        if loyalty_points:
            loyalty_points.is_used = True
            db_session.commit()

        if user:
            db_session.refresh(user)
            if user.is_blocked:
                await user_services.block_user(user_id=user.id, block_time=7)
                block_time = await user_services.block_time(user_id=user.id)
                await cb.bot.send_message(
                    contract.freelancer.telegram_id,
                    f"Пожалуйста, не срывайте дедлайны на будущих задачах и берите в запас чуть больше времени при отклике.\n\n"
                    f"<b>До конца блокировки осталось: {block_time}</b>\nАпелляция: @natfullin",
                )

    if status == "cancel":
        await cb.bot.send_message(
            contract.task.author.telegram_id,
            f"<b>Исполнитель отклонил задачу</b>.\n\n"
            f"<b>Название задачи</b>:  {escape(contract.task.title)}\n"
            f"<b>Описание задачи</b>:  {escape(contract.task.description) if contract.task.description else ''}\n\n"
            f"Исполнитель: {contract.freelancer.full_name} @{contract.freelancer.username}\n"
            f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n\n"
            f"Согласованная сумма договора: {contract.budget} руб.\n\n"
            f"{text_comment_freelancer}",
        )

        await cb.message.edit_text(
            f"<b>Текущая задача</b>:  {escape(contract.task.title)}\n\n"
            f"<b>Описание задачи</b>:  {escape(contract.task.description) if contract.task.description else ''}\n\n"
            f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n\n"
            f"Согласованная сумма договора: {contract.budget} руб.\n\n"
            f"{text_comment_freelancer}",
        )

        contract.status = ContractStatusType.CANCELLED
        contract.cancelled_by_freelancer = True

        all_contracts_by_task_id = crud.get_contracts_by_task_id(session=db_session, task_id=task.id)
        await RatingService.user_rating_change(
            session=db_session,
            users_id=contract.freelancer.id,
            change_direction=RaitingChangeDirection.MINUS,
            score=CANCELTASK_RATING_DECREASE,
            comment=CANCELTASK_RATING_DECREASE_COMMENT
        )


        if all_contracts_by_task_id:
            states = []
            for contract in all_contracts_by_task_id:
                states.append(contract.status)
            if not set(states).__contains__("ATWORK"):
                task.status = TaskStatusType.ACCEPTSOFFERS
        try:
            await scheduler_services.remove_job(contract_id=contract_id)
        except Exception as e:
            print(f"Не удалось удалить джоб {e}")

        db_session.commit()
        await service_manager.rating_services.update_rating_weekly_tasks(user.id)


    if status == "comment":
        await state.set_state(ContractComment.comment)
        msg = await cb.message.answer("<b>Напишите ваш комментарий заказчику.</b>")
        await state.update_data(comment_msg_to_delete=msg.message_id)
        await cb.message.delete()


@r.message(ContractComment.comment)
async def executor_contract_handle_comment(msg, state, db_session):

    data = await state.get_data()

    contract = crud.get_contract_by_id(
        session=db_session, contract_id=data["contract_id"]
    )

    comment_text = msg.text

    contract.comment_freelancer = comment_text

    db_session.commit()

    await msg.bot.delete_message(
        chat_id=msg.chat.id, message_id=data["comment_msg_to_delete"]
    )
    await msg.bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)

    loyalty_points = crud.get_latest_active_loyalty_points(
        db_session, contract.freelancer_id
    )
    points_text = f" + {loyalty_points.amount} баллов" if loyalty_points else ""

    await msg.bot.send_message(
        contract.freelancer.telegram_id,
        f"<b>Текущая задача</b>: {escape(contract.task.title)}\n\n"
        f"<b>Описание задачи</b>: {escape(contract.task.description) if contract.task.description else ''}\n\n"
        f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n\n"
        f"Согласованная сумма договора: {contract.budget} руб.{points_text}\n\n"
        f'{f"Ваш комментарий: {contract.comment_freelancer}" if contract.comment_freelancer else ""}',
        reply_markup=contract_executor_keyboard(contract),
    )

    await state.clear()


# Новые обработчики для разблокировки
@r.callback_query(F.data.startswith('unban_event:'))
async def handle_unban_event(cb: types.CallbackQuery, db_session: Session, state: FSMContext):
    data = cb.data.split(':')
    user_id = int(data[1])
    action = data[2]

    if action == "unban":
        crud.unban_user_by_id(db_session, user_id=user_id)
        await cb.message.edit_text("✅ Пользователь успешно разблокирован")
        await cb.answer()
    elif action == "skip":
        await cb.message.edit_text("⏩ Действие пропущено")
        await cb.answer()

    data = await state.get_data()
    loyalty_mode = data.get('loyalty_mode', False)
    contract_id = data.get('contract_id')
    work_started_at = data.get('work_started_at')
    deadline_at = data.get('deadline_at')
    
    await state.set_state(ContractStates.work_evaluate)
    await state.update_data(
                    loyalty_mode=loyalty_mode,
                    contract_id=contract_id,
                    work_started_at=work_started_at,
                    deadline_at=deadline_at
                )
    await cb.message.answer("Введите оценку от 0 до 10")
    
    db_session.commit()


@r.callback_query(F.data.startswith("myblocks_unban_event:"))
async def handle_myblocks_unban_event(call: types.CallbackQuery, db_session: Session):
    user_id = int(call.data.split(":")[1])
    crud.unban_user_by_id(db_session, user_id=user_id)
    await call.message.edit_text("✅ Пользователь успешно разблокирован")
    await call.answer()
    db_session.commit()


@r.callback_query(F.data.startswith('customer_contract_event:'))
async def customer_contract_callback(cb: types.CallbackQuery, db_session: Session, state: FSMContext, user, service_manager):
    """
    Коллбэк хэндлер заказчика
    """
    try:
        contract_id = int(cb.data.split(":")[1])
        status = cb.data.split(":")[2]

        contract = crud.get_contract_by_id(session=db_session, contract_id=contract_id)
        if not contract:
            await cb.answer("Ошибка: контракт не найден")
            return

        loyalty_points = crud.get_latest_active_loyalty_points(
            db_session, contract.freelancer_id, client_id=contract.task.author_id
        )
        points_text = f" + {loyalty_points.amount} баллов" if loyalty_points else ""

        await state.update_data(contract_id=contract_id)

        if status == 'loyalty':
            contract.status = ContractStatusType.COMPLETED
            contract.task.status = TaskStatusType.COMPLETED
            contract.work_stopped_at = datetime.now()

            try:
                await scheduler_services.remove_job(contract_id=contract_id)
            except Exception as e:
                print(f'Не удалось удалить джоб {e}')

            await RatingService.user_rating_change(
                session=db_session,
                users_id=contract.freelancer_id,
                change_direction=RaitingChangeDirection.PLUS,
                score=FINISH_WORK_RATING_INCREASE,
                comment=FINISH_WORK_RATING_INCREASE_COMMENT,
            )

            await service_manager.rating_services.update_rating_weekly_tasks(user.id)


            db_session.commit()

            try:
                await state.set_state(ContractStates.work_evaluate)
                await state.update_data(
                    loyalty_mode=True,
                    contract_id=contract.id,
                    work_started_at=contract.work_started_at,
                    deadline_at=contract.deadline_at,
                )
                await cb.message.delete()
                await cb.message.answer('Оцените работу от 0 до 10')
            except Exception as e:
                await cb.message.answer(
                    "Пожалуйста, пришлите сумму баллов, которую нужно начислить на счет исполнителя."
                )
            return

        if status == "accept":
            time_for_work = datetime.now() - contract.work_started_at
            await cb.message.delete()
            await state.update_data(contract_id=contract_id)

            await cb.message.answer(
                f"Название задачи: {escape(contract.task.title)}\n"
                f"Вы приняли работу у: {contract.freelancer.full_name} @{contract.freelancer.username}\n"
                f"ID задачи: {contract.task.id}\n"
                f"Согласованная сумма договора: {contract.budget} руб.{points_text}\n"
                f"Время на реализацию задачи (план): {deadline_converted_output(contract.deadline_days)}\n"
                f"Время на реализацию задачи (факт): {time_for_work.days*24 + time_for_work.seconds//3600} ч., "
                f"{time_for_work.seconds%3600//60} м.\n"
                f"Сорван дедлайн: {'Да' if contract.deadline_at<datetime.now() else 'Нет'}\n"
                f"Комментарий исполнителя: {contract.comment_freelancer if contract.comment_freelancer else 'Нет'}"
            )

            await RatingService.user_rating_change(
                session=db_session,
                users_id=contract.freelancer_id,
                change_direction=RaitingChangeDirection.PLUS,
                score=FINISH_WORK_RATING_INCREASE,
                comment=FINISH_WORK_RATING_INCREASE_COMMENT,
            )

            await service_manager.rating_services.update_rating_weekly_tasks(user.id)

            user_data = crud.get_user_by_id(session=db_session, user_id=contract.freelancer_id)
            if user_data.is_blocked:
                msg = await cb.message.answer(
                    text=f"Исполнитель: {contract.freelancer.full_name}\n"
                    "Был заблокирован за срыв дедлайна. Выберите действие:",
                    reply_markup=unban_contract_keyboard(contract.freelancer.id),
                )
                await state.update_data(
                    user_id=contract.freelancer.id,
                    msg_id=msg.message_id,
                    loyalty_mode=False,
                    contract_id=contract.id,
                    work_started_at=contract.work_started_at,
                    deadline_at=contract.deadline_at
                )
                
                await state.set_state(UnbanState.unban_or_not)
            else:
                await cb.message.answer("Оцените работу от 0 до 10")
                await state.set_state(ContractStates.work_evaluate)

            contract.status = ContractStatusType.COMPLETED
            contract.task.status = TaskStatusType.COMPLETED
            contract.work_stopped_at = datetime.now()

            try:
                await scheduler_services.remove_job(contract_id=contract_id)
            except Exception as e:
                print(f"Не удалось удалить джоб {e}")

            db_session.commit()

        if status == 'return':
            contract.status = ContractStatusType.ATWORK
            contract.task.status = TaskStatusType.ATWORK
            db_session.commit()

            await cb.message.edit_text(
                f"<b>Задача выполнена</b>.\n\n"
                f"<b>Название задачи</b>:  {escape(contract.task.title)}\n\n"
                f"<b>Описание задачи</b>:  {escape(contract.task.description) if contract.task.description else ''}\n\n"
                f"Исполнитель: {contract.freelancer.full_name} @{contract.freelancer.username}\n"
                f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n\n"
                f"Согласованная сумма договора: {contract.budget} руб.{points_text}\n\n"
                f"Комментарий исполнителя: {contract.comment_freelancer if contract.comment_freelancer else 'Нет'}",
                reply_markup=contract_customer_comment_keyboard(contract),
            )

            await service_manager.rating_services.update_rating_weekly_tasks(user.id)

        if status == 'comment':
            await cb.message.delete()
            await state.update_data(contract_id=contract_id)
            await cb.message.answer("Сообщение комментария.")
            await state.set_state(ContractStates.contract_return_comment)

        if status == "no_comment":
            contract.task.status = TaskStatusType.ATWORK
            db_session.commit()

            await cb.message.delete()
            await cb.message.answer("Задача возвращена исполнителю...")
            await cb.bot.send_message(
                chat_id=contract.freelancer.telegram_id,
                text=f"<b>Заказчик вернул задачу</b>.\n\n"
                f"<b>Название задачи</b>:  {escape(contract.task.title)}\n\n"
                f"<b>Описание задачи</b>:  {escape(contract.task.description) if contract.task.description else ''}\n\n"
                f"Исполнитель: {contract.freelancer.full_name} @{contract.freelancer.username}\n"
                f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n\n"
                f"Согласованная сумма договора: {contract.budget} руб. {points_text}\n\n"
                f"Комментарий заказчика: без комментариев.\n\n"
                f"Комментарий исполнителя: {contract.comment_freelancer if contract.comment_freelancer else 'Нет'}",
                reply_markup=contract_executor_keyboard(contract),
            )

    except Exception as e:
        print(f"Unexpected error in customer_contract_callback: {e}")
        await cb.answer("Произошла ошибка при обработке запроса")


# Обработчик для текстовых команд в состоянии UnbanState
@r.message(UnbanState.unban_or_not)
async def handle_unban_decision(
    msg: types.Message, state: FSMContext, db_session: Session
):
    data = await state.get_data()
    user_id = data.get("user_id")

    if msg.text == "Разблокировать":
        await user_services.unban_user(user_id)
        await msg.answer("✅ Пользователь успешно разблокирован")
        
    else:
        await msg.answer("⏩ Действие пропущено")

    # Очистка состояния
    await msg.bot.delete_message(chat_id=msg.chat.id, message_id=data["msg_id"])
    await state.clear()


@r.message(ContractStates.work_evaluate)
async def contract_work_evaluate(msg, state: FSMContext, db_session: Session):
    """Стэйт получения оценки и отправки ответа исполнителю"""

    try:
        evaluate = int(msg.text)
        if not (0 <= evaluate <= 10):
            raise ValueError
        
    except ValueError:
        return await msg.answer(
            "Неправильный формат. Число должно быть ЦЕЛЫМ, БЕЗ ПРОБЕЛОВ, ЗАПЯТЫХ И ТОЧЕК, от 0 до 10"
        )

    data = await state.get_data()

    contract_id = data.get("contract_id")
    contract = crud.get_contract_by_id(session=db_session, contract_id=contract_id)

    
    contract.evaluate = evaluate
    loyalty_mode = data.get('loyalty_mode', False)
    db_session.commit()

    
    if loyalty_mode:
        await state.set_state(LoyaltyStates.waiting_for_amount)
        await msg.answer("Введите бонусные баллы")
        return
    else:
        await msg.answer('Результат отправлен исполнителю.')
        await msg.bot.send_message(
            chat_id=contract.freelancer.telegram_id,
            text=
            f"<b>Заказчик принял задачу</b>.\n\n"
            f"<b>Название задачи</b>:  {escape(contract.task.title)}\n\n"
            f"<b>Описание задачи</b>:  {escape(contract.task.description) if contract.task.description else ''}\n\n"
            f"Исполнитель: {contract.freelancer.full_name} @{contract.freelancer.username}\n"
            f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n\n"
            f"Согласованная сумма договора: {contract.budget} руб.\n\n"
            f"Комментарий исполнителя: {contract.comment_freelancer if contract.comment_freelancer else 'Нет'}",
        )
        
    
    await state.clear()


@r.message(ContractStates.contract_return_comment)
async def contract_return_comment(
    msg: types.Message, state: FSMContext, db_session: Session
):
    """Стэйт получения и отправки комментария заказчика"""

    await state.update_data(comment=msg.text)
    data = await state.get_data()

    contract_id = data.get("contract_id")
    contract = crud.get_contract_by_id(session=db_session, contract_id=contract_id)
    comment = data.get("comment")

    if comment:
        await msg.answer("Задача вернулась исполнителю.")
        await msg.bot.send_message(
            chat_id=contract.freelancer.telegram_id,
            text=f"<b>Заказчик вернул задачу</b>.\n\n"
            f"<b>Название задачи</b>:  {escape(contract.task.title)}\n"
            f"<b>Описание задачи</b>:  {escape(contract.task.description) if contract.task.description else ''}\n\n"
            f"Исполнитель: {contract.freelancer.full_name} @{contract.freelancer.username}\n"
            f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n\n"
            f"Согласованная сумма договора: {contract.budget} руб.\n\n"
            f"Комментарий исполнителя: {contract.comment_freelancer if contract.comment_freelancer else 'Нет'}\n\n"
            f"Комментарий заказчика: {comment}\n",
            reply_markup=contract_executor_keyboard(contract),
        )
    await state.clear()


@r.message(LoyaltyStates.waiting_for_amount)
async def handle_points_amount(
    message: types.Message, state: FSMContext, db_session: Session
):
    """Handle points amount input"""
    try:
        amount = int(message.text)
        if amount <= 0:
            await message.answer(
                "Количество баллов должно быть положительным числом. Попробуйте еще раз:"
            )
            return

        await state.update_data(points_amount=amount)
        await message.answer("Введите срок действия баллов в часах:")
        await state.set_state(LoyaltyStates.waiting_for_lifespan)

    except ValueError:
        await message.answer("Пожалуйста, введите корректное число баллов.")


@r.message(LoyaltyStates.waiting_for_lifespan)
async def handle_points_lifespan(message: types.Message, state: FSMContext):
    """Handle points lifespan input"""
    try:
        lifespan_hours = int(message.text)
        if lifespan_hours <= 0:
            await message.answer(
                "Срок действия должен быть положительным числом часов. Попробуйте еще раз:"
            )
            return

        await state.update_data(lifespan_hours=lifespan_hours)
        await message.answer(
            "Сколько напоминаний отправить до сгорания баллов? (от 1 до 10):"
        )
        await state.set_state(LoyaltyStates.waiting_for_notifications)

    except ValueError:
        await message.answer("Пожалуйста, введите корректное число часов.")


@r.message(LoyaltyStates.waiting_for_notifications)
async def handle_notifications_count(
    message: types.Message, state: FSMContext, db_session: Session
):
    """Handle notifications count input and create loyalty points"""
    try:
        notifications = int(message.text)
        if not 1 <= notifications <= 10:
            await message.answer(
                "Количество напоминаний должно быть от 1 до 10. Попробуйте еще раз:"
            )
            return

        data = await state.get_data()
        amount = data["points_amount"]
        lifespan_hours = data["lifespan_hours"]
        contract = crud.get_contract_by_id(db_session, data["contract_id"])

        loyalty_points = crud.get_active_loyalty_points(
            db_session, contract.freelancer_id, client_id=contract.task.author_id
        )
        points_text = f" + {loyalty_points.amount} баллов" if loyalty_points else ""

        expires_at = datetime.now() + timedelta(hours=lifespan_hours)
        points = crud.create_loyalty_points(
            session=db_session,
            user_id=contract.freelancer_id,
            client_id=contract.client_id,
            amount=amount,
            expires_at=expires_at,
            notification_count=notifications,
        )

        await scheduler_services.schedule_loyalty_notifications(
            points_id=points.id, expires_at=expires_at, notification_count=notifications
        )

        work_started_at = data.get("work_started_at")
        time_for_work = (
            datetime.now() - work_started_at if work_started_at else timedelta()
        )

        deadline_at = data.get("deadline_at")
        deadline_missed = (
            "Да" if deadline_at and deadline_at < datetime.now() else "Нет"
        )

        await message.answer(
            f"Готово, вы успешно начислили {amount} баллов исполнителю.\n"
            f"Срок действия баллов: {lifespan_hours} часов.\n"
            f"Количество напоминаний: {notifications} \n\n"
            f"Название задачи: {escape(contract.task.title)}\n"
            f"Вы приняли работу у: {contract.freelancer.full_name} @{contract.freelancer.username}\n"
            f"ID задачи: {contract.task.id}\n"
            f"Согласованная сумма договора: {contract.budget} руб. {points_text}\n"
            f"Время на реализацию задачи (план): {deadline_converted_output(contract.deadline_days)}.\n"
            f"Время на реализацию задачи (факт): {time_for_work.days*24 + time_for_work.seconds//3600} ч., "
            f"{time_for_work.seconds%3600//60} м.\n"
            f"Сорван дедлайн: {deadline_missed}\n"
            f"Комментарий исполнителя: {contract.comment_freelancer if contract.comment_freelancer else 'Нет'}"
        )
        await message.answer('Результат отправлен исполнителю.')
        await message.bot.send_message(
            chat_id=contract.freelancer.telegram_id,
            text=
            f"<b>Заказчик принял задачу</b>.\n\n"
            f"<b>Название задачи</b>:  {escape(contract.task.title)}\n\n"
            f"<b>Описание задачи</b>:  {escape(contract.task.description) if contract.task.description else ''}\n\n"
            f"Исполнитель: {contract.freelancer.full_name} @{contract.freelancer.username}\n"
            f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n\n"
            f"Согласованная сумма договора: {contract.budget} руб.\n\n"
            f"Комментарий исполнителя: {contract.comment_freelancer if contract.comment_freelancer else 'Нет'}",
        )
    

        await message.bot.send_message(
            contract.freelancer.telegram_id,
            f"Вам начислено {amount} баллов лояльности от заказчика {contract.client.full_name}!\n"
            f"Срок действия баллов: {lifespan_hours} часов.\n"
            f"Вы получите {notifications} напоминаний до истечения срока действия баллов.\n"
            f"Баллы будут автоматически использованы в следующей задаче у этого заказчика.",
        )

        await state.clear()

    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")
        