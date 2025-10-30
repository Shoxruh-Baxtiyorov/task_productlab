import asyncio

from bot.services.segment_services import SegmentService
from bot.services.user_services import UserServices
from bot.services.deadline_services import DeadlineServices

from bot.services.scheduler.scheduler_services import SchedulerServices

from bot.services.utils_services import UtilsServices
from bot.services.rating_services import RatingService


class ServicesManager:
    """Класс для управления зависимостями и взаимодействия между сервисами."""
    def __init__(self):
        # Инициализация всех зависимостей
        self.scheduler_services = SchedulerServices()
        self.utils_services = UtilsServices()
        self.user_services = UserServices(
            utils_services=self.utils_services
        )

        self.rating_services = RatingService(
            scheduler_services=self.scheduler_services
        )
        
        self.deadline_services = DeadlineServices(
            user_services=self.user_services,
            scheduler_services=self.scheduler_services,
            utils_services=self.utils_services,
            rating_services=self.rating_services

        )

        self.segment_services = SegmentService(
            scheduler_services=self.scheduler_services,
        )

    def get_user_services(self) -> UserServices:
        """Получить экземпляр UserServices."""
        return self.user_services

    def get_scheduler_services(self) -> SchedulerServices:
        """Получить экземпляр SchedulerServices."""
        return self.scheduler_services

    def get_deadline_services(self) -> DeadlineServices:
        """Получить экземпляр DeadlineServices."""
        return self.deadline_services

    def get_utils_service(self) -> UtilsServices:
        return self.utils_services

    async def load_scheduler_jobs(self):
        methods_dict = {
            'trigger_deadline_actions': self.deadline_services.trigger_deadline_actions,
            'deadline_notification_message': self.deadline_services.deadline_notification_message,
            'monthly_rating_bonus_message': self.rating_services.monthly_rating_bonus_message,
            'monthly_rating_advance_notification': self.rating_services.monthly_rating_advance_notification,
            'rating_weekly_update': self.rating_services.rating_weekly_update,
            'first_weekly_rating_advance_notification': self.rating_services.first_weekly_rating_advance_notification,
            'second_weekly_rating_advance_notification': self.rating_services.second_weekly_rating_advance_notification,
            'third_weekly_rating_advance_notification': self.rating_services.third_weekly_rating_advance_notification,
            'fourth_weekly_rating_advance_notification': self.rating_services.fourth_weekly_rating_advance_notification,
            'fifth_weekly_rating_advance_notification': self.rating_services.fifth_weekly_rating_advance_notification,
            'sixth_weekly_rating_advance_notification': self.rating_services.sixth_weekly_rating_advance_notification,
            'send_resume_reminder': self.rating_services.send_resume_reminder,
        }
        await self.scheduler_services.load_jobs_from_db(methods_dict)

    async def load_cron_jobs(self):
        methods_dict = {
            'monthly_rating_bonus': self.rating_services.monthly_rating_bonus,
            'segment_update': self.segment_services.parse_segments,
            'hourly_not_registered_users': self.user_services.hourly_not_registered_users,
        }
        await self.scheduler_services.load_cron_jobs(methods_dict)

    async def start_scheduler(self):
        await self.scheduler_services.start()

service_manager = ServicesManager()