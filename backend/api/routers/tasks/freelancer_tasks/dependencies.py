from fastapi import Request
from sqlalchemy import and_, or_
from db.models import Task, Contract


async def freelancer_task_parameter(request: Request, task_id: int):
    """
    Прикрепляет автоматически заказ для методов фрилансера по заказам.
    \f
    :param request: запрос
    :param task_id: айди заказа
    :return: объект заказа
    """
    task = request.state.session.query(Task).join(
        Contract, 
        and_(
            Contract.task_id == Task.id,
            Contract.freelancer_id == request.state.user.id
        )
    ).filter(
        Task.id == task_id
    ).first()
    
    return task
