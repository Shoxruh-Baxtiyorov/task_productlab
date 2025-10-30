from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.constants.rating import WORKING_HOURS, USERS_INVOLVEMENT_RATING_DECREASE, USERS_INVOLVEMENT_RATING_DECREASE_COMMENT
from db.database import SessionLocal
from datetime import datetime, timedelta
from db.crud import CommonCRUDOperations
from db.models import User, RaitingChangeDirection
from sqlalchemy.orm import Session

from bot.services.utils_services import UtilsServices
import loader

class UserServices:
    def __init__(self, utils_services: UtilsServices):
        self.crud = CommonCRUDOperations()
        self.utils_services = utils_services

    async def block_user(self, user_id: int, block_time: int):
        """
        Метод блокировки пользователя, устанавливает время блокировки, и статус
        :param user_id: Айди пользователя
        :param block_time: Время на которое нужно заблокировать
        """
        with SessionLocal() as session:
            user = self.crud.get_user_by_id(session, user_id)
            if user:
                user.banned_until = self.current_date + timedelta(days=block_time)
                user.is_blocked = True
                session.commit()
                session.refresh(user)


    async def auto_block_user(self, user_id: int):
        """
        Метод блокировки пользователя, устанавливает время блокировки, и статус
        :param user_id: Айди пользователя
        :param block_time: Время на которое нужно заблокировать
        """
        with SessionLocal() as session:
            user = self.crud.get_user_by_id(session, user_id)
            if user:
                #user.banned_until = self.current_date + timedelta(days=block_time)
                user.is_blocked = True
                session.commit()

    async def unblock_user(self, user_id: int):
        with SessionLocal() as session:
            user = self.crud.get_user_by_id(session, user_id)
            if user:
                session.refresh(user)
                if user.is_blocked:
                    if user.banned_until:
                        if self.current_date > user.banned_until:
                            user.is_blocked = False
                            user.banned_until = None
                            session.commit()

    async def block_time(self, user_id: int):
        with SessionLocal() as session:
            user = self.crud.get_user_by_id(session, user_id)
            if user and user.is_blocked:
                if user.banned_until:
                    time_left = user.banned_until - self.current_date

                    banned_time_end = self.utils_services.time_until(time_left)

                    return banned_time_end

    @property
    def current_date(self):
        """Текущая дата"""
        return datetime.now()

    @staticmethod
    async def handle_user_blocked_bot(session: Session, user_id: int):
        """
        Centralized handler for when a user blocks the bot.
        Sets user as dead, sets rating to 0 with comment, and decreases referrer's rating.
        
        :param session: Database session
        :param user_id: User ID (not telegram_id)
        """
        from bot.services.rating_services import RatingService
        
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return
            
        user.is_dead = True
        
        # Get current rating score to set it to 0
        rating = user.rating
        if rating and rating.score > 0:
            current_score = int(rating.score)
            # Use RatingService to properly decrease rating to 0 with comment
            await RatingService.user_rating_change(
                session=session,
                users_id=user.id,
                change_direction=RaitingChangeDirection.MINUS,
                score=current_score,
                comment="Пользователь заблокировал бота"
            )
        
        # Handle referrer rating decrease
        if user.reff_telegram_id:
            ref_user = session.query(User).filter(User.telegram_id == user.reff_telegram_id).first()
            if ref_user:
                await RatingService.user_rating_change(
                    session=session,
                    users_id=ref_user.id,
                    change_direction=RaitingChangeDirection.MINUS,
                    score=USERS_INVOLVEMENT_RATING_DECREASE,
                    comment=USERS_INVOLVEMENT_RATING_DECREASE_COMMENT
                )
        
        session.commit()
        print(f"Пользователь {user.full_name} ({user.telegram_id}) заблокировал бота. Рейтинг обнулен.")

    @classmethod
    def get_not_registered_users_message(cls):
        return (
                "⚠️Вы не закончили регистрацию!\n"
                + "Пройдите регистрацию в системе до конца, и начинайте зарабатывать"
                + "или искать исполнителей уже сейчас 💰!"
        )

    async def hourly_not_registered_users(self):

        with SessionLocal() as session:
            telegram_ids = self.crud.get_not_registered_users_hour_ago(session=session)
            for x in telegram_ids:
                try:
                    await loader.bot.send_message(
                        x,
                        self.get_not_registered_users_message(),
                        reply_markup=InlineKeyboardMarkup(
                                inline_keyboard=[
                                    [InlineKeyboardButton(
                                        text="Продолжить регистрацию",
                                        url=f"{loader.BOT_ADDRESS}?start=continue"
                                    )]
                                ]
                            )
                    )
                except TelegramForbiddenError:
                    # User blocked the bot - find user by telegram_id and handle
                    user = session.query(User).filter(User.telegram_id == x).first()
                    if user:
                        await UserServices.handle_user_blocked_bot(session, user.id)
                except TelegramBadRequest as e:
                    print(f"Ошибка отправки сообщения пользователю ({x}): {e}")
