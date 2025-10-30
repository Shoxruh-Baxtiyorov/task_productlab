from aiogram import Router, F
from sqlalchemy import and_

from db.models import *


r = Router()


async def set_user_relation(db_session, user_id, related_user_id, status):
    user_relation = db_session.query(UserRelation).filter(
        and_(UserRelation.user_id == user_id, UserRelation.related_user_id == related_user_id)).first()
    if not user_relation:
        user_relation = UserRelation(
            user_id=user_id,
            related_user_id=related_user_id,
            status=status
        )
        db_session.add(user_relation)
    else:
        user_relation.status = status
    db_session.commit()


@r.callback_query(F.data.startswith('turn_off_not'))
async def turn_off_not_handler(cb, db_session, user):
    related_user_id = int(cb.data.replace('turn_off_not:', ''))
    await set_user_relation(db_session, user.id, related_user_id, UserRelationStatusType.HIDE_OFFERS)
    await cb.message.edit_reply_markup(None)
    await cb.answer('⚠️Уведомления от пользователя скрыты')


@r.callback_query(F.data.startswith('block_user'))
async def block_user_handler(cb, db_session, user):
    related_user_id = int(cb.data.replace('block_user:', ''))
    await set_user_relation(db_session, user.id, related_user_id, UserRelationStatusType.BLOCKED)
    await cb.message.edit_reply_markup(None)
    await cb.answer('⚠️Пользователь заблокирован')
