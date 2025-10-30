from fastapi import Request
from sqlalchemy import and_

from db.models import Offer


async def offer_parameter(request: Request, offer_id: int):
    """
    Зависимость для эндпоинтов откликов, чтобы отклики сразу брались из БД

    :param request: Запрос пользователя
    :param offer_id: Айди отклика
    :return: Объект отклика из базы
    """
    return request.state.session.query(Offer).filter(
        and_(Offer.id == offer_id, Offer.task.has(author_id=request.state.user.id))).first()
