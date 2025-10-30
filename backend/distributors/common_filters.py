from db.models import UserRelation, UserRelationStatusType
from sqlalchemy import and_, or_


def filter_task_notif_by_relations(task, sub, session):
    return not session.query(UserRelation).filter(
        and_(
            or_(
                and_(
                    UserRelation.user_id == sub.user_id,
                    UserRelation.related_user_id == task.author_id
                ).self_group(),
                and_(
                    UserRelation.user_id == task.author_id,
                    UserRelation.related_user_id == sub.user_id
                ).self_group()
            ).self_group(),
            or_(
                UserRelation.status == UserRelationStatusType.HIDE_OFFERS,
                UserRelation.status == UserRelationStatusType.BLOCKED
            ).self_group()
        )
    ).first()
