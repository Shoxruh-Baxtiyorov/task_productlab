from aiogram import Router, F
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent, Message

from bot.services.user_services import UserServices
from db.database import SessionLocal
from db.models import User

r = Router()


@r.error(ExceptionTypeFilter(TelegramForbiddenError), F.update.message.as_("message"))
async def error_handler(event: ErrorEvent, message: Message):
    with SessionLocal() as session:
        telegram_id = event.from_user.id
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            await UserServices.handle_user_blocked_bot(session, user.id)
