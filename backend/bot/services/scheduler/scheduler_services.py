from datetime import datetime, timedelta
from uuid import uuid4

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.services.document_parser import DocumentParser
from bot.services.s3_services import S3Services
from bot.keyboards.resume_keyboards import question_keyboard
from db.database import SessionLocal
from db.models import Resume, SchedulerTask, LoyaltyPoints, User
from sqlalchemy import and_

from bot.services.scheduler.cron_jobs import monthly_rating_bonus, segment_update, hourly_not_registered_users
import loader 


class SchedulerServices:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SchedulerServices, cls).__new__(cls, *args, **kwargs)
            cls._instance.scheduler = AsyncIOScheduler()
        return cls._instance

    def add_job(self, object_id: int, task_name: str, run_date: datetime, method, method_name: str,
                      interval = None,
                      message_id = None,
                      args = None
                      ):
        """
        Метод добавления задач на выполнение в определенную дату
        :param object_id: Это может быть айди любого нужного объекта из базы, например Task, Contract, User
        :param task_name: Это название самой задачи в базе
        :param run_date: Дата выполнения
        :param method: Метод который нужно выполнить
        :param method_name: Название метода для выполнения
        :param message_id: Если нужно сохранить айди сообщения в тг
        :param interval: Если нужно хранить высчитанный интервал
        :param args: Дополнительные аргументы для метода
        """

        job_id = str(uuid4())

        with SessionLocal() as session:
            task = SchedulerTask(
                object_id=object_id,
                job_id=job_id,
                task_name=task_name,
                deadline_date=run_date,
                method_name=method_name,
                interval_hours=interval,
                last_message_id=message_id,
            )
            session.add(task)
            session.commit()

        job = self.scheduler.add_job(
            method,
            trigger='date',
            run_date=run_date,
            id=job_id,
            args=args or [object_id, job_id],
        )

        return job

    async def remove_job(self, contract_id: str):
        with SessionLocal() as session:
            try:
                jobs = session.query(SchedulerTask).filter(and_(SchedulerTask.object_id == contract_id)).all()
                for job in jobs:
                    self.scheduler.remove_job(job_id=job.job_id)
                    session.query(SchedulerTask).filter(and_(SchedulerTask.job_id == job.job_id)).delete()
                    session.commit()
            except Exception as e:
                print(f'Не удалось удалить джоб ремувджоб {e}')
                


    async def load_jobs_from_db(self, methods_dict):
        with SessionLocal() as session:
            scheduler_tasks = session.query(SchedulerTask).filter_by(is_completed=False).all()
            now = datetime.utcnow()
            
            print(f"Found {len(scheduler_tasks)} tasks in db for donwload")

            for scheduler_task in scheduler_tasks:
                method_name = scheduler_task.method_name
                method_to_call = methods_dict.get(method_name)

                if not method_to_call:
                    print(f"Method {method_name} not found in methods_dict")
                    continue

                existing_job = self.scheduler.get_job(scheduler_task.job_id)
                if existing_job:
                    print(f"Task {scheduler_task.job_id} already in scheduler, skiping")
                    continue

                if scheduler_task.deadline_date < now:
                    print(f"Task {scheduler_task.job_id} expired, moving")

                    #Логика обработки пропущенных задач
                    new_run_date = now + timedelta(minutes=5)   # Переносим задачу на 5 минут вперёд
                    self.scheduler.add_job(
                        method_to_call,
                        'date',
                        run_date=new_run_date,
                        id=scheduler_task.job_id,
                        args=[scheduler_task.object_id, scheduler_task.job_id],
                    )

                    scheduler_task.deadline_date = new_run_date

                else:
                    print(f"Donwloading task {scheduler_task.job_id} on {scheduler_task.deadline_date}")
                    self.scheduler.add_job(
                        method_to_call,
                        'date',
                        run_date=scheduler_task.deadline_date,
                        id=scheduler_task.job_id,
                        args=[scheduler_task.object_id, scheduler_task.job_id],
                    )

            # Commit all changes at once after processing all tasks
            session.commit()
            
            # Clean up completed tasks
            session.query(SchedulerTask).filter_by(is_completed=True).delete()
            session.commit()

    def shutdown(self):
        """Остановить планировщик."""
        self.scheduler.shutdown(wait=False)

    async def start(self):
        """Асинхронный запуск планировщика."""
        self.scheduler.start()


    async def load_cron_jobs(self, methods_dict):
        monthly_rating_bonus['func'] = methods_dict.get('monthly_rating_bonus')
        self.scheduler.add_job(**monthly_rating_bonus)
        segment_update['func'] = methods_dict.get('segment_update')
        self.scheduler.add_job(**segment_update)
        hourly_not_registered_users['func'] = methods_dict.get('hourly_not_registered_users')
        self.scheduler.add_job(**hourly_not_registered_users)

    async def schedule_loyalty_notifications(self, points_id: int, expires_at: datetime, notification_count: int):
        """
        Планирует уведомления о сгорании баллов лояльности
        
        :param points_id: ID записи баллов лояльности
        :param expires_at: Дата истечения срока
        :param notification_count: Количество уведомлений
        """
        now = datetime.now()
        total_seconds = (expires_at - now).total_seconds()
        interval_seconds = total_seconds / notification_count

        for i in range(notification_count):
            notification_time = now + timedelta(seconds=interval_seconds * (i + 1))
            
            is_last = i == notification_count - 1
            
            self.add_job(
                object_id=points_id,
                task_name=f"loyalty_notification_{points_id}_{i}",
                run_date=notification_time,
                method=self.send_loyalty_notification,
                method_name="send_loyalty_notification",
                args=[points_id, is_last]
            )

    async def send_loyalty_notification(self, points_id: int, is_last: bool):
        """
        Отправляет уведомление о баллах лояльности
        
        :param points_id: ID записи баллов лояльности
        :param is_last: Является ли это последним уведомлением
        """
        with SessionLocal() as session:
            points = session.query(LoyaltyPoints).filter(LoyaltyPoints.id == points_id).first()
            if not points or points.is_used:
                return

            if is_last:
                points.is_used = True
                session.commit()
                
                message = (
                    f"❌ Ваши баллы лояльности ({points.amount}) сгорели!\n"
                    f"Срок действия истек."
                )
            else:
                time_left = points.expires_at - datetime.now()
                total_seconds = time_left.total_seconds()
                
                if total_seconds < 3600:  
                    minutes_left = int(total_seconds / 60)
                    time_str = f"{minutes_left} минут"
                elif total_seconds < 86400:
                    hours_left = int(total_seconds / 3600)
                    time_str = f"{hours_left} часов"
                else:
                    days_left = int(total_seconds / 86400)
                    time_str = f"{days_left} дней"
                
                message = (
                    f"⚠️ Напоминание о баллах лояльности!\n"
                    f"У вас есть {points.amount} неиспользованных баллов.\n"
                    f"До сгорания осталось: {time_str}"
                )

            try:
                await loader.bot.send_message(
                    points.user.telegram_id,
                    message
                )
            except Exception as e:
                print(f"Failed to send loyalty notification: {e}")

    #  async def send_resume_question_to_users(self):
    #      """
    #      Отправляет клавиатуру с вопрос о новой подписке
    #      """
    #      async def _send_and_update():

    #          s3_client = S3Services()


    #          with SessionLocal() as session:
    #              users = (
    #          session.query(User)
    #          .filter(User.checked_resume == False)
    #          .join(Resume, Resume.user_id == User.id)
    #          .filter(Resume.is_active == True)
    #          .all()
    #      )

    #              for user in users:
    #                  try:
    #                      resume = next((r for r in user.resumes if r.is_active))
    #                      if not resume:
    #                          continue 

    #                      file_content = await s3_client.get_file(resume.file_url.split("/")[-1])
                        
    #                      parsed_text = DocumentParser.parse_document(file_content, resume.file_type)
                        
    #                      if not parsed_text:
    #                          print(f"Resume by user is empty")
    #                          continue

    #                      if "Навыки" in parsed_text:
    #                          try:
    #                              skills_text = parsed_text.split("Навыки")[-1].split("Дополнительная")[0].strip()
    #                              final = [s for s in skills_text.split() if s.strip()]

    #                              if len(final) > 0:
    #                                  update_skills(db_session, final, user)
    #                                  await state.update_data(resume_skills=final)

                                        
    #                                  await loader.bot.send_message(
    #                                      chat_id=user.telegram_id,
    #                                      text = f"""Мы обнаружили у вас {len(final)} доп.сегментов по вашему документу.
    #                                      \nХотите чтобы мы вам создали сегменты и подписки по вашим навыкам?
    #                                      \n{{{", ".join(final)}}}""",
    #                                      reply_markup=question_keyboard()
    #                                  )


    #                          except Exception as e:
    #                              print(f"Error send message to user {user.telegram_id}: {e}")

    #      await _send_and_update()