from datetime import timedelta
from typing import Type, List
from sqlalchemy import text, extract, BigInteger
from sqlalchemy import or_
from sqlalchemy.sql import func
from sqlalchemy.orm import Session

from bot.utils.deadline_utils import deadline_converted_output

from .models import *
from .models import Contract, Task, Offer


class CommonCRUDOperations:
    @staticmethod
    def create_offer(session: Session, **kwargs) -> Offer:
        offer = Offer(**kwargs)
        session.add(offer)
        session.commit()

        CommonCRUDOperations.create_message(
            session,
            author_id=offer.author_id,
            receiver_id=offer.task.author_id,
            context=MessageContextType.OFFER,
            source=MessageSourceType.BOT,
            type=MessageType.MESSAGE,
            text=f"{offer.description}\n\nБюджет: {offer.budget}₽\nСрок: {deadline_converted_output(offer.deadline_days)}",
            offer_id=offer.id
        )

        return offer

    @staticmethod
    def get_offer_by_id(session: Session, offer_id) -> Type[Offer] | None:
        return session.query(Offer).where(Offer.id == offer_id).first()

    @staticmethod
    def get_offer_by_task_id(session: Session, task_id) -> Type[Offer] | None:
        return session.query(Offer).where(Offer.task_id == task_id).first()

    @staticmethod
    def get_offers_by_task_id(session: Session, task_id) -> List[Offer] | None:
        return session.query(Offer).where(Offer.task_id == task_id).all()

    @staticmethod
    def get_contract_by_offer_id(session: Session, offer_id) -> Type[Contract] | None:
        return session.query(Contract).where(Contract.offer_id == offer_id).first()

    @staticmethod
    def get_offer_count_by_user_id(session: Session, user_id: int) -> int:
        return session.query(func.count()).filter(Offer.author_id == user_id).scalar()

    @staticmethod
    def get_offer_any_participant_by_id(session: Session, user, offer_id) -> Type[Offer] | None:
        return session.query(Offer).where(
            and_(
                or_(
                    Offer.author_id == user.id,
                    Offer.task.has(author_id=user.id)
                ).self_group(),
                Offer.id == offer_id
            )
        ).first()

    @staticmethod
    def get_task_any_participant_by_id(session: Session, user, task_id) -> Type[Task] | None:
        return session.query(Task).where(
            and_(
                or_(
                    Task.author_id == user.id,
                    Task.freelancer_id == user.id
                ).self_group(),
                Task.id == task_id
            )
        ).first()

    @staticmethod
    def create_message(session: Session, **kwargs) -> Message:
        msg = Message(**kwargs)
        session.add(msg)
        session.commit()

        return msg

    @staticmethod
    def get_my_message_by_id(session, user, message_id) -> Message:
        return session.query(Message).where(
            and_(
                Message.author_id == user.id,
                Message.id == message_id
            )
        ).where(Message.is_deleted != True).first()

    @staticmethod
    def create_message_file(session: Session, **kwargs) -> MessageFile:
        msg_file = MessageFile(**kwargs)
        session.add(msg_file)
        session.commit()

        return msg_file

    @staticmethod
    def get_contracts_by_user_id(session: Session, user_id) -> list[Type[Contract]]:
        return session.query(Contract).where(Contract.freelancer_id == user_id).all()

    @staticmethod
    def get_contract_count_by_user_id(session: Session, user_id: int) -> int:
        return session.query(func.count()).filter(Contract.freelancer_id == user_id).scalar()

    @staticmethod
    def get_contract_count_by_user_and_client(session: Session, user_id: int, author_id: int) -> int:
        return session.query(func.count()).filter(Contract.freelancer_id == user_id, Contract.client_id == author_id).scalar()

    @staticmethod
    def get_contract_sum_by_user_and_client(session: Session, user_id: int, author_id: int) -> int:
        return session.query(func.sum(Contract.budget)).filter(Contract.freelancer_id == user_id, Contract.client_id == author_id).scalar() or 0

    @staticmethod
    def get_contract_by_id(session: Session, contract_id) -> Type[Contract] | None:
        return session.query(Contract).where(Contract.id == contract_id).first()


    @staticmethod
    def get_contract_by_task_id(session: Session, task_id: int) -> Type[Contract] | None:
        return session.query(Contract).where(Contract.task_id == task_id).first()

    @staticmethod
    def get_contracts_by_task_id(session: Session, task_id) -> List[Contract] | None:
        return session.query(Contract).filter(
            Contract.task_id == task_id,
            or_(
                Contract.status == ContractStatusType.ATWORK,
                Contract.status == ContractStatusType.INSPECTED
            )
        ).all()

    # Tasks GRUDs
    @staticmethod
    def get_task_by_id(session: Session, task_id) -> Type[Task] | None:
        return session.query(Task).where(Task.id == task_id).first()

    @staticmethod
    def get_tasks_by_status(session: Session, status) -> list[Type[Task] | None]:
        return session.query(Task).filter(Task.status == status).all()

    # User GRUDs
    @staticmethod
    def get_user_by_id(session: Session, user_id) -> Type[User]:
        return session.query(User).where(User.id == user_id).first()

    @staticmethod
    def unban_user_by_id(session: Session, user_id: int) -> None:
        session.query(User).where(User.id == user_id).update({"is_blocked": False, "banned_until": None})
        session.commit()

    @staticmethod
    def get_banned_users_by_customer(session: Session, customer_id: int) -> Type[None] | None:
        client = session.query(User.id).filter(User.telegram_id == customer_id).first()
        if not client:
            return []
            
        result = session.query(
                User.id,
                User.username,
                User.full_name,
                func.count(Contract.id).label("tasks_count"),
                User.banned_until
                ).join(
                Contract, User.id == Contract.freelancer_id
                ).where(
                or_(
                    User.is_blocked == True,
                    User.banned_until > func.now()
                ),
                Contract.client_id == client.id
                ).group_by(
                User.id,
                User.username,
                User.full_name,
                User.banned_until
                )
        return result

    # @staticmethod
    # def get_not_registered_users_hour_ago(session: Session):
    #
    #     hour_ago = datetime.now() - timedelta(hours=1)
    #     print(hour_ago.year, hour_ago.month, hour_ago.hour, hour_ago.minute)
    #     query = session.query(User.telegram_id).filter(
    #         and_(
    #             User.telegram_id > 0,
    #             hour_ago.year == extract('year', User.created_at),
    #             hour_ago.month == extract('month', User.created_at),
    #             hour_ago.day == extract('day', User.created_at),
    #             hour_ago.hour == extract('hour', User.created_at),
    #             hour_ago.minute == extract('minute', User.created_at),
    #         )
    #     )
    #     return session.scalars(query).all()

    @staticmethod
    def get_not_registered_users_hour_ago(session: Session, time_window_minutes: int = 5):
        """
        Возвращает telegram_id пользователей, которые:
        - начали регистрацию (telegram_id > 0),
        - не завершили её (is_registered = False),
        - были созданы примерно 1 час назад (±time_window_minutes минут).

        Параметры:
            session: SQLAlchemy сессия
            time_window_minutes: Допустимое отклонение в минутах (по умолчанию ±5 минут)
        """
        now = datetime.now()
        exact_hour_ago = now - timedelta(hours=1)
        start_time = exact_hour_ago - timedelta(minutes=time_window_minutes)
        end_time = exact_hour_ago + timedelta(minutes=time_window_minutes)

        query = session.query(User.telegram_id).filter(
            User.telegram_id > 0,
            User.is_registered == False,
            User.created_at.between(start_time, end_time)  # Диапазон: 1 час назад ±5 мин
        )
        return session.scalars(query).all()

    @staticmethod
    def create_loyalty_points(session: Session, user_id: int, client_id: int, amount: int, expires_at: datetime, notification_count: int) -> LoyaltyPoints:
        """Create new loyalty points record"""
        points = LoyaltyPoints(
            user_id=user_id,
            client_id=client_id,
            amount=amount,
            expires_at=expires_at,
            notification_count=notification_count
        )
        session.add(points)
        session.commit()
        return points

    @staticmethod
    def get_active_loyalty_points(session: Session, user_id: int, client_id: int = None) -> LoyaltyPoints | None:
        """Get unexpired and unused loyalty points for user"""
        query = session.query(LoyaltyPoints).filter(
            and_(
                LoyaltyPoints.user_id == user_id,
                LoyaltyPoints.expires_at > datetime.now()
            )
        )
        
        if client_id is not None:
            query = query.filter(LoyaltyPoints.client_id == client_id)
            
        return query.order_by(LoyaltyPoints.created_at.desc()).first()

    @staticmethod
    def get_latest_active_loyalty_points(session: Session, user_id: int, client_id: int = None) -> LoyaltyPoints | None:
        """Get latest unexpired and unused loyalty points for user from specific client"""
        query = session.query(LoyaltyPoints).filter(
            and_(
                LoyaltyPoints.user_id == user_id,
                LoyaltyPoints.is_used == False,
                LoyaltyPoints.expires_at > datetime.now()
            )
        )
        
        if client_id is not None:
            query = query.filter(LoyaltyPoints.client_id == client_id)
            
        return query.order_by(LoyaltyPoints.created_at.desc()).first()

    @staticmethod
    def create_resume(session: Session, **kwargs) -> Resume:
        """Create new resume record"""
        resume = Resume(**kwargs)
        session.add(resume)
        session.commit()
        return resume

    @staticmethod
    def get_active_resume(session: Session, user_id: int) -> Resume | None:
        """Get user's active resume"""
        return session.query(Resume).filter(
            and_(
                Resume.user_id == user_id,
                Resume.is_active == True
            )
        ).first()

    @staticmethod
    def deactivate_old_resumes(session: Session, user_id: int) -> None:
        """Deactivate all user's resumes"""
        session.query(Resume).filter(
            Resume.user_id == user_id
        ).update({"is_active": False})
        session.commit()
