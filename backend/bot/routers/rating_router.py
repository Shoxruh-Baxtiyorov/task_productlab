from datetime import datetime, timedelta
from decimal import Decimal

from aiogram import Router, F, types
from aiogram.filters import Command

from bot.keyboards.rating_service_keyboards import info_rating_keyboard
from bot.services.rating_services import RatingService

from db.models import User, Rating, RatingHistory, RaitingChangeDirection

from bot.constants.rating import *
from sqlalchemy.orm import Session


r = Router(name='rating_router')


@r.callback_query(F.data.startswith("bonus_"))
async def rating_query(callback: types.CallbackQuery, db_session):
    message_datetime = callback.data.split("_")[1]
    await callback.message.delete_reply_markup()
    if message_datetime < str(datetime.now() - timedelta(hours=1)):
        await callback.answer("Срок действия предложения истек")
    else:
        user = db_session.query(User).where(User.telegram_id == callback.from_user.id).first()
        await RatingService.user_rating_change(
            db_session,
            user.id,
            RaitingChangeDirection.PLUS,
            MONTHLY_RATING_BONUS,
            MONTHLY_RATING_BONUS_COMMENT
        )

@r.message(Command('rating'))
async def check_user_rating(message: types.Message, db_session: Session, user):
    if not user:
        return
    rating = db_session.query(Rating).where(Rating.user_id == user.id).first()
    if not rating:
        await message.answer("Скорее всего Вы не закончили процесс регистрации, поэтому вам не начислен бонус. Рейтинг - 0.")
        return
    rating_history = db_session.query(RatingHistory).where(RatingHistory.user_id == user.id).all()
    message_text = (
        f"Ваш рейтинг - <b>{Decimal(rating.score)}</b>.\n"
        f"История изменения:\n"
    )
    if rating_history:
        for el in rating_history:
            message_text += f"<b>{el.change_direction} {el.score}</b>  => {el.comment}\n\n"
    
    await message.answer(message_text, reply_markup=info_rating_keyboard())


@r.callback_query(F.data == 'info_rating')
async def info_rating(cb: types.CallbackQuery):
    await cb.message.delete()
    await cb.message.answer(TEXT_RATING_INFO)