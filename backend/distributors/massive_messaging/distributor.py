import asyncio

from db.models import (
    User,
    Distribution,
    NotificationType,
    RatingHistory,
    Rating,
    RaitingChangeDirection,
)
from bot.services.user_services import UserServices

from sqlalchemy import or_, and_
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

import loader


async def deploy_new_distribution(distribution: Distribution, db_session):
    """
    Метод отправки рассылки всем пользователям
    :param distribution: Объект рассылки
    :param db_session: Сессия БД
    """
    # получаем список пользователей, у которых включены уведомления платформы и которые относятся к выбранным ролям
    receivers = (
        db_session.query(User)
        .filter(
            and_(
                or_(*[User.roles.contains([role]) for role in distribution.roles]),
                User.notification_types.contains([NotificationType.PLATFORM]),
            )
        )
        .all()
    )

    deads_count = 0  # ведем учет мертвых
    sent = 0  # учёт реально отправленных
    for receiver in receivers:
        try:
            await loader.bot.copy_message(
                receiver.telegram_id,
                from_chat_id=distribution.message_chat_id,
                message_id=distribution.message_id,
            )
            sent += 1
        except TelegramForbiddenError:
            await UserServices.handle_user_blocked_bot(db_session, receiver.id)
            deads_count += 1
        except TelegramBadRequest as e:
            print(f"[{receiver.telegram_id}]: {e}")

        await asyncio.sleep(
            0.5
        )  # задержка, т.к. есть ограничение на отправку сообщений в сек. в telegram

    # уведомляем о завершении рассылки
    await loader.bot.send_message(
        distribution.author.telegram_id,
        f"Рассылка <b>#{distribution.id}</b> завершена\n\n"
        f"<b>Всего получателей:</b> {len(receivers)}\n"
        f"<b>Успешно отправлено:</b> {sent}\n"
        f"<b>Мертвые души:</b> {deads_count}",
        reply_to_message_id=distribution.message_id,
    )
