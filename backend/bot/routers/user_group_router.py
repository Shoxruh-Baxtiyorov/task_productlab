from decimal import Decimal
from bot.keyboards.create_task_keyboards import *
from db.models import Rating, User, Task, RoleType, NotificationType

async def user_group_registration(event, db_session , group_user: User, owner):
    if not group_user or not group_user.is_registered:
        if not group_user:
            user = User(
                telegram_id=event.chat.id,
                username=event.chat.username,
                full_name=event.chat.title,
                is_registered=True,
                roles=[RoleType.CLIENT],
                owner_id=owner.telegram_id,
            )
            
            
            db_session.add(user)
            db_session.flush()

            user_rating = Rating(user_id=user.id, 
                                 score=Decimal('10'))
            
            db_session.add(user_rating)
            
            db_session.commit()
            await event.answer(
                "Группа успешно зарегистрирована.",
            )

