import asyncio
from datetime import datetime, timedelta, time
from functools import partial
from html import escape

from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from db.database import SessionLocal
from db.models import (
    Contract,
    User,
    ContractStatusType,
    RaitingChangeDirection,
    SchedulerTask,
)

from db.crud import CommonCRUDOperations

from bot.constants.rating import (
    DEADLINE_RATING_DECREASE,
    DEADLINE_RATING_DECREASE_COMMENT,
)
from bot.services.scheduler.scheduler_services import SchedulerServices
from bot.services.user_services import UserServices
import pytz

import loader

from bot.keyboards.contract_keyboard import contract_executor_keyboard
from bot.services.rating_services import RatingService
from bot.services.utils_services import UtilsServices
from sqlalchemy import and_


class DeadlineServices:
    def __init__(self, user_services: UserServices, scheduler_services: SchedulerServices, utils_services: UtilsServices, rating_services: RatingService):
        self.user_services = user_services
        self.scheduler_services = scheduler_services
        self.utils_services = utils_services
        self.rating_services = rating_services
        self.bot = loader.bot
        self.moscow_tz = pytz.timezone("Europe/Moscow")
        self.crud = CommonCRUDOperations()

    async def trigger_deadline_actions(self, contract_id: int, job_id):
        """
        Проверяем, не прошел ли срок дедлайна, если прошел, блокируем юзера
        :param contract_id: Айди пользователя
        :param job_id:
        """
        with SessionLocal() as session:
            contract = self.crud.get_contract_by_id(session, contract_id)
            if contract.status == ContractStatusType.ATWORK:
                await RatingService.user_rating_change(
                    session,
                    contract.freelancer_id,
                    RaitingChangeDirection.MINUS,
                    DEADLINE_RATING_DECREASE,
                    DEADLINE_RATING_DECREASE_COMMENT,
                )
                await self.user_services.auto_block_user(contract.freelancer_id)

            job = (
                session.query(SchedulerTask)
                .filter(and_(SchedulerTask.job_id == job_id))
                .first()
            )

            job.is_completed = True
            session.commit()
            if job.is_completed:
                try:
                    session.query(SchedulerTask).filter(
                        SchedulerTask.job_id == job_id
                    ).delete()
                    session.commit()
                except Exception as e:
                    print(f'Не удалось удалить джоб {e}')
            await self.rating_services.update_rating_weekly_tasks(contract.freelancer_id)
            await self.rating_services.update_rating_weekly_tasks(contract.client_id)

    async def set_deadline_notification(
        self, contract_id: int, task_id: int, task_name: str, method_name: str
    ):
        with SessionLocal() as session:
            contract = self.crud.get_contract_by_id(session, contract_id)
            task = self.crud.get_task_by_id(session, task_id)

            # Дата дедлайна
            deadline_at = contract.deadline_at.astimezone(self.moscow_tz)

            # Рассчитываем текущее время
            now = datetime.now(pytz.utc).astimezone(self.moscow_tz)

            # Количество напоминаний
            total_reminders = task.number_of_reminders

            # Вычисляем общее время до дедлайна в секундах
            time_until_deadline = (deadline_at - now).total_seconds()

            # Интервал между напоминаниями
            interval_seconds = time_until_deadline / total_reminders

            now += timedelta(seconds=interval_seconds)

            # Добавляем первую задачу
            self.scheduler_services.add_job(
                object_id=contract_id,
                task_name=task_name,
                run_date=now,
                method=self.deadline_notification_message,
                method_name=method_name,
                interval=interval_seconds,
            )

    async def deadline_notification_message(self, contract_id: int, job_id: str):
        with SessionLocal() as session:
            sent_message = None

            job = (
                session.query(SchedulerTask)
                .filter(
                    and_(
                        SchedulerTask.job_id == job_id,
                        SchedulerTask.task_name
                        == "notification",  # Дополнительный критерий
                    )
                )
                .first()
            )

            contract = self.crud.get_contract_by_id(session, job.object_id)

            # Текущее время в Москве
            now = datetime.now(pytz.utc).astimezone(self.moscow_tz)

            deadline_at = contract.deadline_at
            time_left = deadline_at - self.current_date

            # Параметры рабочего времени
            start_time = time(9, 0)  # 9:00 утра
            end_time = time(22, 0)  # 22:00 вечера
            # Если текущее время в пределах рабочего времени, отправляем уведомление
            if start_time <= now.time() <= end_time:

                deadline_time = self.utils_services.time_until(time_left)

                # Проверяем что контракт в статусе работы
                if contract is None or contract.status != ContractStatusType.ATWORK: 
                    return
                
                # Удаление старого сообщения
                if job.last_message_id:
                    try:
                        await self.bot.delete_message(
                            chat_id=contract.freelancer.telegram_id,
                            message_id=job.last_message_id,
                        )
                    except Exception as e:
                        pass

                # Отправка нового сообщения
                try:
                    sent_message = await self.bot.send_message(
                        chat_id=contract.freelancer.telegram_id,
                        text=(
                            f"<b>Текущая задача</b>: {escape(contract.task.title)}\n\n"
                            f"<b>Описание задачи</b>: {escape(contract.task.description) if contract.task.description else ''}\n\n"
                            f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n\n"
                            f"Согласованная сумма договора: {contract.budget} руб.\n\n"
                            f"<b>На выполнение этой задачи осталось:</b> {deadline_time}"
                        ),
                        reply_markup=contract_executor_keyboard(contract),
                    )
                except TelegramForbiddenError:
                    # Если бот заблокирован пользователем
                    from bot.services.user_services import UserServices
                    await UserServices.handle_user_blocked_bot(session, contract.freelancer.id)
                except TelegramBadRequest as e:
                    # Если есть проблемы с форматом сообщения (например, некорректная разметка)
                    pass
                    # При необходимости отправьте упрощенное сообщение без разметки

            else:
                pass

            # Рассчитываем интервал для следующего уведомления
            interval_seconds = job.interval_hours

            # Рассчитываем следующее время для уведомления
            next_run_time = now + timedelta(seconds=interval_seconds)

            # Убедимся, что следующее время попадет в рабочие часы (если оно выходит за пределы, переназначаем на следующий день)
            if next_run_time.time() < start_time:
                next_run_time = next_run_time.replace(
                    hour=start_time.hour,
                    minute=start_time.minute,
                    second=0,
                    microsecond=0,
                )
            elif next_run_time.time() > end_time:
                next_run_time = next_run_time.replace(
                    hour=start_time.hour,
                    minute=start_time.minute,
                    second=0,
                    microsecond=0,
                ) + timedelta(days=1)
            if sent_message:
                message_id = sent_message.message_id
            else:
                message_id = None

            # Добавляем новую задачу с пересчитанным временем
            self.scheduler_services.add_job(
                object_id=contract_id,
                task_name=job.task_name,
                run_date=next_run_time,
                method=self.deadline_notification_message,
                method_name=job.method_name,
                interval=interval_seconds,
                message_id=message_id,
            )
            job.is_completed = True
            session.commit()
            if job.is_completed:
                try:
                    session.query(SchedulerTask).filter(
                        SchedulerTask.job_id == job_id
                    ).delete()
                    session.commit()
                except Exception as e:
                    print(f"Не удалось удалить джоб {e}")

    async def set_deadline(
        self,
        contract_id: int,
        task_name: str,
        deadline_date: datetime,
        method_name: str,
    ):
        self.scheduler_services.add_job(
            object_id=contract_id,
            task_name=task_name,
            method=self.trigger_deadline_actions,
            run_date=deadline_date,
            method_name=method_name,
        )

    @property
    def current_date(self):
        """Текущая дата"""
        return datetime.now()
