from aiogram import BaseMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import or_
from db.database import SessionLocal
from db.models import User
import loader

from bot.routers.user_group_router import user_group_registration


class IsRegistrationCheckMiddleware(BaseMiddleware):
    """
    Данный мидлвар предназначен для того, чтобы проверять регистрацию пользователя.\n
    """

    async def __call__(self, handler, event, data):
        """
        Срабатывание мидлваря

        :param handler: вызываемый хендлер
        :param event: событие обновления
        :param data: данные передаваемые в хендлер
        :return: None
        """
        with SessionLocal() as session:
            if event.migrate_to_chat_id:
                new_chat_id = event.migrate_to_chat_id
                old_chat_id = event.chat.id
                group_username = event.chat.username
                user = session.query(User).filter(User.telegram_id == old_chat_id).first()

                if group_username:
                    user.username = group_username
                    session.commit()

                if user:
                    user.telegram_id = new_chat_id
                    session.commit()
            else:
                if event.chat.type == 'private':
                    return await handler(event, data)
                else:
                    user = session.query(User).filter(User.telegram_id == event.from_user.id).first()
                    group_user = session.query(User).filter(User.telegram_id == event.chat.id).first()
                    
                    try:
                        if not user or not user.is_registered:
                            has_registered_user = session.query(User).filter(
                                User.is_registered == True
                            ).first() is not None

                            if not has_registered_user:
                                keyboard = InlineKeyboardMarkup(
                                    inline_keyboard=[
                                        [InlineKeyboardButton(
                                            text="Запуск",
                                            url=f"{loader.BOT_ADDRESS}?start"
                                        )]
                                    ]
                                )
                                await event.answer(
                                    "Для регистрации перейдите в личные сообщения:",
                                    reply_markup=keyboard
                                )
                                return
                    except Exception as e:
                        pass
                    else:
                        if event.chat.type == 'group' or event.chat.type == 'supergroup':
                            if user and user.is_registered:
                                if not group_user or not group_user.is_registered:
                                    await user_group_registration(event, session, group_user, user)
                                else:
                                    return await handler(event, data)