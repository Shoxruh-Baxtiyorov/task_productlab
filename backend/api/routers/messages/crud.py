from db.models import *
from sqlalchemy import or_, and_


class CRUD:
    @staticmethod
    def get_task_last_message(session, user, inter_id, task_id):
        return session.query(Message).where(
            and_(
                or_(
                    and_(
                        Message.author_id == user.id,
                        Message.receiver_id == inter_id
                    ).self_group(),
                    and_(
                        Message.receiver_id == user.id,
                        Message.author_id == inter_id
                    ).self_group()
                ).self_group(),
                or_(
                    Message.task_id == task_id,
                    Message.offer.has(task_id=task_id)
                ).self_group()
            )
        ).order_by(Message.id.desc()).first()

    @staticmethod
    def delete_message(session, message):
        message.is_deleted = True
        session.commit()

    @staticmethod
    def get_my_message_by_id(session, user, message_id):
        return session.query(Message).filter(
            and_(
                Message.id == message_id,
                Message.author_id == user.id
            )
        ).first()

    @staticmethod
    def query_offer_messages(session, user, offer, interlocutor_id):
        return session.query(Message).where(
            and_(
                Message.offer_id == offer.id,
                or_(
                    and_(
                        Message.author_id == interlocutor_id,
                        Message.receiver_id == user.id
                    ).self_group(),
                    and_(
                        Message.receiver_id == interlocutor_id,
                        Message.author_id == user.id
                    ).self_group()
                ).self_group(),
                Message.is_deleted != True
            )
        )

    @staticmethod
    def query_task_messages(session, user, task, interlocutor_id):
        return session.query(Message).where(
            and_(
                Message.task_id == task.id,
                or_(
                    and_(
                        Message.author_id == interlocutor_id,
                        Message.receiver_id == user.id
                    ).self_group(),
                    and_(
                        Message.receiver_id == interlocutor_id,
                        Message.author_id == user.id
                    ).self_group()
                ).self_group(),
                Message.is_deleted != True
            )
        )

    @staticmethod
    def get_interlocutors_crud(session, user):
        return session.query(
            case(
                (
                    (Message.author_id == user.id, Message.receiver_id)
                ),
                else_=Message.author_id
            )
        ).distinct().all()

    @staticmethod
    def get_last_message_crud(session, user, inter_id):
        return session.query(Message).where(
            or_(
                and_(
                    Message.author_id == user.id,
                    Message.receiver_id == inter_id
                ).self_group(),
                and_(
                    Message.receiver_id == user.id,
                    Message.author_id == inter_id
                ).self_group()
            )
        ).order_by(Message.id.desc()).first()
