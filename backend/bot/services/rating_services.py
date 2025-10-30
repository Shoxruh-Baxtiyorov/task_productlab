import asyncio
import calendar
from datetime import timedelta, datetime
from decimal import Decimal
from random import randint
from typing import List

from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.types import ReplyKeyboardMarkup

from db.crud import CommonCRUDOperations
from db.database import SessionLocal

import loader

from db.models import (
    User,
    Task,
    Contract,
    Rating,
    RatingHistory,
    RaitingChangeDirection,
    SchedulerTask,
)
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from bot.constants.rating import *

from bot.services.scheduler.scheduler_services import SchedulerServices

from bot.keyboards.rating_service_keyboards import rating_bonus_button


class RatingService:
    def __init__(self, scheduler_services: SchedulerServices):
        self.crud = CommonCRUDOperations()
        self.scheduler_services = scheduler_services

    @staticmethod
    async def user_rating_change(
        session: Session,
        users_id: int | List[int],
        change_direction: str,
        score: int,
        comment: str,
    ) -> None:
        """
        Изменение рейтинга пользователя
        :session: сессия
        :user_id: id пользователя чей рейтинг должен быть изменен
        :change_direction: направление изменения рейтинга "+" или "-"
        :score: на сколько должен быть инменен рейтинг
        :comment: комментарий к изменению для истории ризменения
        """
        if isinstance(users_id, List):
            for user_id in users_id:
                await RatingService.user_rating_change(
                    session, user_id, change_direction, score, comment
                )
            return
        user_rating = session.query(Rating).where(
            Rating.user_id == users_id).one_or_none()
        
        if user_rating is None:
            user_rating = Rating(user_id=users_id, score=Decimal('10'))
            session.add(user_rating)
            session.flush()
            
        if change_direction == RaitingChangeDirection.MINUS:
            if user_rating.score >= score:
                user_rating.score = (
                            user_rating.score - score) 
            else:
                session.rollback()
                return
        elif change_direction == RaitingChangeDirection.PLUS:
            user_rating.score += Decimal(score)

        session.add(RatingHistory(
            user_id=users_id,
            change_direction=change_direction,
            score=score,
            comment=comment
        ))
        session.commit()

        user = session.query(User).where(User.id == users_id).one_or_none()
        try:
            await loader.bot.send_message(
                user.telegram_id,
                f"Ваш рейтинг изменен.\n"
                f"{change_direction} {score} - {comment}\n"
                f"Рейтинг - {round(user_rating.score, 2)}",
            )
        except TelegramForbiddenError:
            # Note: We don't call handle_user_blocked_bot here to avoid infinite recursion
            # since this method is called BY handle_user_blocked_bot
            print(f"Пользователь {user.full_name} ({user.telegram_id}) заблокировал бота.")
        except TelegramBadRequest as e:
            print(f"Ошибка отправки сообщения пользователю {user.full_name} ({user.telegram_id}): {e}")

    @staticmethod
    async def complete_job(session: Session, job_id):
        job = (
            session.query(SchedulerTask)
            .where(SchedulerTask.job_id == job_id)
            .one_or_none()
        )
        if job is None:
            return
        job.is_completed = True
        session.commit()
        if job.is_completed:
            try:
                session.query(SchedulerTask).filter(
                    SchedulerTask.job_id == job_id
                ).delete()
                session.commit()
            except Exception as e:
                print(f"Не удалось удалить джоб комплит {e}")

    async def monthly_rating_bonus_message(self, user_id: int, job_id):
        with SessionLocal() as session:
            user = session.query(User).where(User.id == user_id).one_or_none()
            try:
                await loader.bot.send_message(
                    user.telegram_id,
                    f"Забери бонус сейчас и получи {MONTHLY_RATING_BONUS} балл к рейтингу\n"
                    f"Предложение действительно в течении 1 часа",
                    reply_markup=rating_bonus_button(datetime.now()),
                )
            except TelegramForbiddenError:
                from bot.services.user_services import UserServices
                await UserServices.handle_user_blocked_bot(session, user.id)
            except TelegramBadRequest as e:
                print(f"Ошибка отправки сообщения пользователю {user.full_name} ({user.telegram_id}): {e}")
            await self.complete_job(session, job_id)

    async def monthly_rating_advance_notification(self, user_id: int, job_id):
        with SessionLocal() as session:
            user = session.query(User).where(User.id == user_id).one_or_none()
            try:
                await loader.bot.send_message(
                    user.telegram_id,
                    f"Сегодня Вы получите сообщение с бонусом. Предложение будет активно в течении 1 часа. Не упусти его!!!",
                )
            except TelegramForbiddenError:
                from bot.services.user_services import UserServices
                await UserServices.handle_user_blocked_bot(session, user.id)
            except TelegramBadRequest as e:
                print(f"Ошибка отправки сообщения пользователю {user.full_name} ({user.telegram_id}): {e}")
            await self.complete_job(session, job_id)

    async def monthly_rating_bonus(self):
        month = datetime.now().month
        year = datetime.now().year
        last_day = calendar.monthrange(year, month)[1]
        with SessionLocal() as session:
            users = (
                session.query(User)
                .where(
                    and_(
                        User.is_dead == False,
                        User.is_blocked == False,
                        User.owner_id == None,
                    )
                )
                .all()
            )
            for user in users:
                day = randint(1, last_day)
                hour = randint(WORKING_HOURS[0], WORKING_HOURS[1])
                minute = randint(0, 59)
                date = datetime(
                    year=year, month=month, day=day, hour=hour, minute=minute
                )
                await self.scheduler_services.add_job(
                    user.id,
                    f"Ежемесячный бонус к рейтингу пользователя {user.id}",
                    date,
                    self.monthly_rating_bonus_message,
                    "monthly_rating_bonus_message",
                )
                notif_date = datetime(
                    year=year, month=month, day=day, hour=WORKING_HOURS[0], minute=0
                )
                await self.scheduler_services.add_job(
                    user.id,
                    f"Предупреждение о ежемесячном бонусе пользователя {user.id}",
                    notif_date,
                    self.monthly_rating_advance_notification,
                    "monthly_rating_advance_notification",
                )


    @staticmethod
    async def send_message(user: User, message: str, reply_markup: ReplyKeyboardMarkup = None):
        from bot.services.user_services import UserServices
        try:
            await loader.bot.send_message(
                user.telegram_id,
                message,
                reply_markup=reply_markup
            )
        except TelegramForbiddenError:
            # Create a session to handle blocked user
            with SessionLocal() as session:
                await UserServices.handle_user_blocked_bot(session, user.id)
            raise
        except TelegramBadRequest as e:
            print(f"Ошибка отправки сообщения пользователю {user.full_name} ({user.telegram_id}): {e}")
            raise


    async def add_weekly_rating_tasks(self, user_id: int):
        weekly_rating_task_names = self.weekly_rating_task_names()
        with SessionLocal() as session:
            jobs = session.query(SchedulerTask).where(and_(
                SchedulerTask.object_id == user_id,
                SchedulerTask.method_name.in_(weekly_rating_task_names)
            )).all()
            if jobs:
                await self.remove_weekly_rating_tasks(user_id, "add_weekly")
                
            
            tasks = []
            now = datetime.now()

            # Первое предупреждение за 6 дней до списания
            self.scheduler_services.add_job(
                user_id,
                f"Первое предупреждение о бездействии {user_id}",
                now + timedelta(days=1),
                self.first_weekly_rating_advance_notification,
                "first_weekly_rating_advance_notification",
            )

            # Второе предупреждение за 5 дней до списания
            self.scheduler_services.add_job(
                user_id,
                f"Второе предупреждение о бездействии {user_id}",
                now + timedelta(days=2),
                self.second_weekly_rating_advance_notification,
                "second_weekly_rating_advance_notification",
            )

            # Третье предупреждение за 4 дня до списания
            self.scheduler_services.add_job(
                user_id,
                f"Третье предупреждение о бездействии {user_id}",
                now + timedelta(days=3),
                self.third_weekly_rating_advance_notification,
                "third_weekly_rating_advance_notification",
            )

            # Четвертое предупреждение за 3 дня до списания
            self.scheduler_services.add_job(
                user_id,
                f"Четвертое предупреждение о бездействии {user_id}",
                now + timedelta(days=4),
                self.fourth_weekly_rating_advance_notification,
                "fourth_weekly_rating_advance_notification",
            )

            # Пятое предупреждение за 2 дня до списания
            self.scheduler_services.add_job(
                user_id,
                f"Пятое предупреждение о бездействии {user_id}",
                now + timedelta(days=5),
                self.fifth_weekly_rating_advance_notification,
                "fifth_weekly_rating_advance_notification",
            )

            # Шестое предупреждение за 1 день до списания
            self.scheduler_services.add_job(
                user_id,
                f"Шестое предупреждение о бездействии {user_id}",
                now + timedelta(days=6),
                self.sixth_weekly_rating_advance_notification,
                "sixth_weekly_rating_advance_notification",
            )
            
            # Само списание через 7 дней
            self.scheduler_services.add_job(
                user_id,
                f"Снижение рейтинга в связи с бездействием {user_id}",
                now + timedelta(days=7),
                self.rating_weekly_update,
                "rating_weekly_update",
            )
            
            # ------- Нет смысла в этом гезере, таски не awaitable ------ не нужно пихать асинхрон туда где это не нжуно
            # await asyncio.gather(*tasks)


    @staticmethod
    def weekly_rating_task_names():
        return [
            "rating_weekly_update",
            "first_weekly_rating_advance_notification",
            "second_weekly_rating_advance_notification",
            "third_weekly_rating_advance_notification",
            "fourth_weekly_rating_advance_notification",
            "fifth_weekly_rating_advance_notification",
            "sixth_weekly_rating_advance_notification"
        ]
    
    async def remove_weekly_rating_tasks(self, user_id: int, string: str = "Default"):
        weekly_rating_task_names = self.weekly_rating_task_names()
        
        with SessionLocal() as session:
            jobs = session.query(SchedulerTask).where(and_(
                SchedulerTask.object_id == user_id,
                SchedulerTask.method_name.in_(weekly_rating_task_names)
            )).all()

            print(f"Was found for delete: {len(jobs)}")
            for job in jobs:
                print(f"Deleting: {job.method_name}")
                try:
                    self.scheduler_services.scheduler.remove_job(
                        job_id=job.job_id)
                    session.delete(job)
                except Exception as e:
                    print(f'Не удалось удалить джоб ремув have called by {string} {e}')
            
            session.commit()
            print("Commit completed")

    async def update_rating_weekly_tasks(self, user_id: id):
        await self.remove_weekly_rating_tasks(user_id, "update")
        await self.add_weekly_rating_tasks(user_id)


    async def rating_weekly_update(self, user_id: int, job_id):
        with SessionLocal() as session:
            user = session.query(User).where(User.id == user_id, User.is_dead == False).one_or_none()
            if not user:
                await self.complete_job(session, job_id)
                return
            await self.user_rating_change(
                session,
                user.id,
                RaitingChangeDirection.MINUS,
                WEEKLY_RATING_DECREASE,
                WEEKLY_RATING_DECREASE_COMMENT
            )
            await self.complete_job(session, job_id)
            await self.add_weekly_rating_tasks(user_id)


    async def first_weekly_rating_advance_notification(self, user_id: int, job_id):
        with SessionLocal() as session:
            user = session.query(User).where(User.id == user_id).one_or_none()
            await self.send_message(
                user,
                f"Через 6 дней ваш рейтинг будет снижен в связи с бездействием."
            )
            await self.complete_job(session, job_id)

    async def second_weekly_rating_advance_notification(self, user_id: int, job_id):
        with SessionLocal() as session:
            user = session.query(User).where(User.id == user_id).one_or_none()
            await self.send_message(
                user,
                f"Через 5 дней ваш рейтинг будет снижен в связи с бездействием."
            )
            await self.complete_job(session, job_id)

    async def third_weekly_rating_advance_notification(self, user_id: int, job_id):
        with SessionLocal() as session:
            user = session.query(User).where(User.id == user_id).one_or_none()
            await self.send_message(
                user,
                f"Через 4 дня ваш рейтинг будет снижен в связи с бездействием."
            )
            await self.complete_job(session, job_id)


    async def fourth_weekly_rating_advance_notification(self, user_id: int, job_id):
        with SessionLocal() as session:
            user = session.query(User).where(User.id == user_id).one_or_none()
            await self.send_message(
                user,
                f"Через 3 дня ваш рейтинг будет снижен в связи с бездействием."
            )
            await self.complete_job(session, job_id)


    async def fifth_weekly_rating_advance_notification(self, user_id: int, job_id):
        with SessionLocal() as session:
            user = session.query(User).where(User.id == user_id).one_or_none()
            await self.send_message(
                user,
                f"Через 2 дня ваш рейтинг будет снижен в связи с бездействием."
            )
            await self.complete_job(session, job_id)


    async def sixth_weekly_rating_advance_notification(self, user_id: int, job_id):
        with SessionLocal() as session:
            user = session.query(User).where(User.id == user_id).one_or_none()
            await self.send_message(
                user,
                f"Через 1 день ваш рейтинг будет снижен в связи с бездействием."
            )
            await self.complete_job(session, job_id)

    async def add_resume_reminder_tasks(self, user_id: int):
        """
        Создает 6 задач для напоминания о загрузке резюме.
        Отправляет уведомления каждые 10 минут в течение 1 часа.
        
        :param user_id: ID пользователя
        """
        now = datetime.now()
        
        # Создаем 6 напоминаний с интервалом в 10 минут
        for i in range(6):
            notification_time = now + timedelta(minutes=10 * (i + 1))
            self.scheduler_services.add_job(
                user_id,
                f"Напоминание о загрузке резюме {user_id}",
                notification_time,
                self.send_resume_reminder,
                "send_resume_reminder",
            )

    async def send_resume_reminder(self, user_id: int, job_id):
        """
        Отправляет напоминание о загрузке резюме с кнопкой 'У меня нет резюме'
        
        :param user_id: ID пользователя
        :param job_id: ID задачи в планировщике
        """
        from bot.keyboards.resume_keyboards import resume_reminder_keyboard
        from db.models import RoleType
        
        with SessionLocal() as session:
            user = session.query(User).where(User.id == user_id).one_or_none()
            if not user:
                await self.complete_job(session, job_id)
                return
            
            # Проверяем, является ли пользователь фрилансером
            if RoleType.FREELANCER not in user.roles:
                # Отменяем напоминания для не-фрилансеров
                await self.remove_resume_reminder_tasks(user_id)
                await self.complete_job(session, job_id)
                return
            
            # Проверяем, загрузил ли пользователь уже резюме
            from db.models import Resume
            active_resume = session.query(Resume).filter(
                Resume.user_id == user_id,
                Resume.is_active == True
            ).first()
            
            if active_resume:
                # Если резюме уже загружено, отменяем дальнейшие напоминания
                await self.remove_resume_reminder_tasks(user_id)
                await self.complete_job(session, job_id)
                return
            
            try:
                await loader.bot.send_message(
                    user.telegram_id,
                    "📄 Пожалуйста, загрузите ваше резюме используя команду /me\n\n"
                    "🎁 За загрузку резюме вы получите 2 балла к рейтингу!",
                    reply_markup=resume_reminder_keyboard()
                )
            except TelegramForbiddenError:
                from bot.services.user_services import UserServices
                await UserServices.handle_user_blocked_bot(session, user.id)
            except TelegramBadRequest as e:
                print(f"Ошибка отправки сообщения пользователю {user.full_name} ({user.telegram_id}): {e}")
            
            await self.complete_job(session, job_id)

    async def remove_resume_reminder_tasks(self, user_id: int):
        """
        Удаляет все задачи напоминания о резюме для пользователя
        
        :param user_id: ID пользователя
        """
        with SessionLocal() as session:
            jobs = session.query(SchedulerTask).filter(
                and_(
                    SchedulerTask.object_id == user_id,
                    SchedulerTask.method_name == "send_resume_reminder"
                )
            ).all()

            print(f"Найдено задач напоминания о резюме для удаления: {len(jobs)}")
            for job in jobs:
                try:
                    self.scheduler_services.scheduler.remove_job(job_id=job.job_id)
                    session.delete(job)
                except Exception as e:
                    print(f'Не удалось удалить задачу напоминания о резюме: {e}')
            
            session.commit()
            print("Удаление задач напоминания о резюме завершено")
