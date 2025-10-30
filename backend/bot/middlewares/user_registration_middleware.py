import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, types
from sqlalchemy.orm import Session

from bot.services.s3_services import S3Services
from db.models import User


class UserRegistrationMiddleware(BaseMiddleware):
    """Middleware для регистрации пользователей и обработки входящих сообщений"""

    async def __call__(
            self,
            handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
            event: types.Message | types.CallbackQuery,
            data: Dict[str, Any]
    ) -> Awaitable:
        """
        Конструктор мидлваера по регистрации пользователей и обработке сообщений

        :param handler: Следующий обработчик в цепочке middleware
        :param event: Входящее сообщение или колбэк
        :param data: Контекстные данные, передаваемые между middleware
        :return: Хендлер с данными о пользователе
        """
        db_session: Session = data['db_session']
        user_id = event.from_user.id

        # Получаем или создаем пользователя
        user = db_session.query(User).filter(User.telegram_id == user_id).first()

        if not user:
            # Извлекаем параметр старта для новых пользователей
            start_parameter = None
            if isinstance(event, types.Message) and event.text and event.text.startswith('/start'):
                # Извлекаем все после "/start " (7 символов)
                if len(event.text) > 7:
                    start_parameter = event.text[7:].strip()
                    logging.info(f"Captured start parameter for new user {user_id}: {start_parameter}")
                else:
                    logging.debug(f"User {user_id} started bot without parameter")
            
            user = User(
                telegram_id=user_id,
                username=event.from_user.username,
                full_name=event.from_user.full_name,
                registration_start_parameter=start_parameter,
            )

            # Сохраняем аватарку при создании пользователя
            if isinstance(event, types.Message):
                await self._save_profile_photo(event, user)

            db_session.add(user)
            try:
                db_session.commit()
                logging.info(f"Successfully registered user {user_id}")
                data['user'] = user

            except Exception as e:
                logging.error(f"Error registering user {user_id}: {e}")
                db_session.rollback()
                raise

        else:
            logging.debug(f"User {user_id} already exists")

        # Сохраняем последнюю команду
        if isinstance(event, types.Message) and event.text and event.text.startswith('/'):
            data['last_command'] = event.text
            logging.debug(f"Saved last command for user {user_id}: {event.text}")

        return await handler(event, data)

    @staticmethod
    async def _save_profile_photo(event: types.Message, user: User) -> None:
        """
        Сохраняет фото профиля в S3 хранилище

        :param event: Входящее сообщение или колбэк
        :param user: Пользователь из базы данных
        """
        try:
            photos = await event.from_user.get_profile_photos()

            if photos.photos:
                photo_id = photos.photos[0][-1].file_id

                file_info = await event.bot.get_file(photo_id)
                file = await event.bot.download_file(file_info.file_path)

                object_name = f'profile-photo.{file_info.file_path.split(".")[-1]}'
                s3_client = S3Services()

                user.profile_photo_url = await s3_client.upload_file(
                    object_name=object_name,
                    file=file,
                    user_id=user.telegram_id
                )
                logging.info(f"Successfully uploaded profile photo for user {user.telegram_id}")
            else:
                logging.debug(f"No profile photos found for user {user.telegram_id}")
        except Exception as e:
            logging.error(f"Error saving profile photo for user {user.telegram_id}: {e}", exc_info=True)
            raise
