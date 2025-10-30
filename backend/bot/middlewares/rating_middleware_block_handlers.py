from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from db.database import SessionLocal
from db.models import User

from bot.constants.rating import MIN_RATING_FOR_WORK


class RatingCheckMiddleware(BaseMiddleware):
    """
    Данный мидлвар предназначен для того, чтобы проверять доступность
    хэндлеров при 0 рейтинге.
    """

    async def __call__(self, handler, event, data):
        """
        Срабатывание мидлваря

        :param handler: вызываемый хендлер
        :param event: событие обновления
        :param data: данные передаваемые в хендлер
        :return: None
        """
        blocked_commands = [
            "/newtask",
            "/newhardtask"
        ]
        with SessionLocal() as session:
            user = session.query(User).where(
                User.telegram_id == event.from_user.id).first()
            if not user:
                pass
            rating = user.rating if user else None
        if rating and rating.score < MIN_RATING_FOR_WORK:
            if isinstance(event, Message):
                if event.html_text.lower() in blocked_commands:
                    await event.answer(f"Ваш рейтинг - {rating.score}. "
                                          f"Он слишком низок для выполнения "
                                      f"команды.\n Подымите Ваш рейтинг.")
                else:
                    await handler(event, data)
            elif isinstance(event, CallbackQuery):
                if event.data.startswith("make_offer"):
                    await event.answer(f"Ваш рейтинг - {rating.score}. "
                                       f"Он слишком низок для выполнения "
                                       f"команды.\nПодымите Ваш рейтинг.")
                else:
                    await handler(event, data)
            else:
                await handler(event, data)
        else:
            await handler(event, data)
