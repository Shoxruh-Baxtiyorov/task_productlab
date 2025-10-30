import logging
from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from db.database import SessionLocal
from db.models import User

from bot.services.services_manager import service_manager


class DefaultMiddleware(BaseMiddleware):
    """
    Данный мидлвар предназначен для того, чтобы предварительно создавать сессию в БД для каждого хендлера.\n
    Так же предоставляет готовый объект User пользователя, от которого поступило обновление
    """
    async def __call__(
            self,
            handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Awaitable:
        """
        Срабатывание мидлваря

        :param handler: вызываемый хендлер
        :param event: событие обновления
        :param data: данные передаваемые в хендлер
        :return: Хендлер с данными о пользователе
        """
        with SessionLocal() as session:
            # Получаем ID пользователя
            if isinstance(event, Message):
                user = session.query(User).filter(User.telegram_id == event.chat.id).first()
            elif isinstance(event, CallbackQuery):
                user = session.query(User).filter(User.telegram_id == event.message.chat.id).first()

            # Передаём данные в хендлер
            data['db_session'] = session
            data['user'] = user
            data['service_manager'] = service_manager

            logging.debug(f"Middleware передаёт управление хендлеру (user={user})")
            return await handler(event, data)
