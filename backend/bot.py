import logging
import asyncio

import loader
from aiogram import Dispatcher

from bot.constants.rating import LOGGING
from bot.functions.send_message_safely import SafeBot
from bot.services.services_manager import ServicesManager
from bot.routers.start_router import r as start_router
from bot.routers.create_task_router import r as create_task_router
from bot.routers.subscribe_router import r as subscribe_router
from bot.routers.task_offer_router import r as task_offer_router
from bot.routers.user_relations_router import r as user_relations_router
from bot.routers.admin_router import r as admin_router
from bot.routers.profile_router import r as profile_router
from bot.routers.contracts_router import r as contracts_router
from bot.routers.rating_router import r as rating_router
from bot.routers.lite_task_router import r as lite_task_router
from bot.routers.error_handlers import r as error_handlers
from bot.routers.unban_contract_router import r as unban_contract_router
from bot.routers.loyalty_router import r as loyalty_router
from bot.routers.resume_router import r as resume_router
from bot.middlewares.default_middleware import DefaultMiddleware
from bot.middlewares.is_registration_check_middleware import IsRegistrationCheckMiddleware
from bot.middlewares.rating_middleware_block_handlers import RatingCheckMiddleware
from bot.middlewares.user_registration_middleware import UserRegistrationMiddleware
from bot.middlewares.db_middleware import DatabaseMiddleware
from db.schedulers import job_auto_archiving_task
from bot.services.auto_archiving import archive_task

logging.basicConfig(**LOGGING)


# Инициализация бота и диспетчера
bot = SafeBot(loader.TOKEN, parse_mode='HTML')
dp = Dispatcher()


async def main():
    """
    Мейн функция запуска бота.
    Добавляем роутеры в диспетчера, регистрируем миддлвари и начинаем проверять обновления.
    """
    logging.info(await bot.get_me())
    dp.include_routers(
        error_handlers,
        rating_router,
        start_router,
        resume_router,
        create_task_router,
        subscribe_router,
        task_offer_router,
        user_relations_router,
        admin_router,
        profile_router,
        contracts_router,
        unban_contract_router,
        loyalty_router,
        lite_task_router,
    )

    # подключаем middleware для работы с БД
    dp.message.outer_middleware(DatabaseMiddleware())
    dp.callback_query.outer_middleware(DatabaseMiddleware())
    
    # подключаем middleware для проверки подписки
    dp.message.outer_middleware(UserRegistrationMiddleware())
    dp.callback_query.outer_middleware(UserRegistrationMiddleware())
    
    service_manager = ServicesManager()
    await service_manager.load_scheduler_jobs()
    await service_manager.load_cron_jobs()
    await service_manager.start_scheduler()
    await archive_task(bot)
    job_auto_archiving_task(bot)
    dp.message.outer_middleware(IsRegistrationCheckMiddleware())
    dp.message.outer_middleware(DefaultMiddleware())
    dp.callback_query.outer_middleware(DefaultMiddleware())
    dp.message.outer_middleware(RatingCheckMiddleware())
    dp.callback_query.outer_middleware(RatingCheckMiddleware())
    await dp.start_polling(bot)



if __name__ == '__main__':
    asyncio.run(main())
