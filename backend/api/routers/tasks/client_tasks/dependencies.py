from fastapi import Request
from sqlalchemy import and_

from db.models import Task


async def client_task_parameter(request: Request, task_id: int):
    """
    Прикрепляет автоматически заказ для методов фрилансера по заказам.
    \f
    :param request: запрос
    :param task_id: айди заказа
    :return: объект заказа
    """
    return request.state.session.query(Task).filter(
        and_(
            Task.id == task_id,
            Task.author_id == request.state.user.id
        )
    ).first()
