import datetime

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import and_, func
from typing import List, Annotated

from db.models import *
from api.routers.tasks.client_tasks.schemas import TaskGetSchema
from api.routers.offers.client_offers.schemas import GetOffersSchema
from api.routers.offers.client_offers.dependencies import offer_parameter

router = APIRouter(tags=['Client offers'])

offer_not_found_response = JSONResponse({'error': 'Offer not found.'}, status_code=404)


@router.get('', response_model=List[GetOffersSchema])
async def my_offers(
        request: Request,
        token: str,
        task_id: int | None = None,
        offset: int | None = None,
        limit: int | None = None):
    """
    Получить отклики, все или по конкретному заказу
    \f
    :param token: Токен для авторизации
    :param request: Запрос пользователя
    :param task_id: Необязательный айди заказа, по которому берутся отклики
    :param offset: оффсет получаемых откликов
    :param limit: ограничить колво возвращаемых откликов
    :return: Список найденных откликов
    """
    q = request.state.session.query(Offer).filter(Offer.task.has(author_id=request.state.user.id))
    if task_id:
        q = q.filter(Offer.task.has(id=task_id))
    if offset:
        q = q.offset(offset)
    if limit:
        q = q.limit(limit)
    return q.all()


@router.post('/{offer_id}/status')
async def change_offer_status(request: Request, token: str, offer: Annotated[dict, Depends(offer_parameter)], status: OfferStatusType):
    """
    Изменить статус отклика. Можно отклонить, добавить в выборку
    \f
    :param token: Токен для авторизации
    :param request: Запрос пользователя
    :param offer: объект отклика
    :param status: новый статус отклика
    :return: 200 или 404
    """
    if not offer:
        return offer_not_found_response
    offer.status = status
    request.state.session.commit()
    return {'ok': f'Offer status changed to {status}'}


@router.post('/{offer_id}/disallow')
async def disallow_offers(request: Request, token: str, offer: Annotated[dict, Depends(offer_parameter)]):
    """
    Заблокировать фрилансера откликаться на мои заказы
    \f
    :param token: Токен для авторизации
    :param request: Запрос пользователя
    :param offer: объект отклика
    :return: 200 or 404
    """
    if not offer:
        return offer_not_found_response
    user_relation = request.state.session.query(UserRelation).filter(
        UserRelation.user_id == request.state.user.id).filter(UserRelation.related_user_id == offer.author_id).first()
    if not user_relation:
        user_relation = UserRelation(
            user_id=request.state.user.id,
            related_user_id=offer.author_id
        )
        request.state.session.add(user_relation)
    user_relation.status = UserRelationStatusType.DISALLOW_OFFERS
    request.state.session.commit()
    return {'ok': 'This user is not allowed to send offers.'}


@router.post('/{offer_id}/accept')
async def accept_offer(request: Request, token: str, offer: Annotated[Offer, Depends(offer_parameter)], source: MessageSourceType = MessageSourceType.WEB):
    """
    Принять отклик в работу
    \f
    :param token: Токен для авторизации
    :param request: Запрос пользователя
    :param offer: Объект отклика
    :return: Заказ
    """
    if not offer:
        return offer_not_found_response
    # меняем статус отклика на ПРИНЯТ
    offer.status = OfferStatusType.ACCEPTED
    offer_task = offer.task
    # остальным откликам по задаче меняем статус на ОТКАЗАНО
    for o in offer_task.offers:
        if o.id != offer.id:
            o.status = OfferStatusType.REJECTED

    # меняем статус задачи на В РАБОТЕ и устанавливаем соответствующие значения
    offer_task.status = TaskStatusType.ATWORK
    offer_task.freelancer_id = offer.author_id

    contract = Contract(
        freelancer_id=offer.author_id,
        client_id=offer_task.author_id,
        offer_id=offer.id,
        task_id=offer_task.id,
        budget=offer.budget,
        deadline_days=offer.deadline_days,
        work_started_at=datetime.now()
    )

    message = Message(
        author_id=request.state.user.id,
        receiver_id=offer.author_id,
        type=MessageType.ACCEPTOFFER,
        context=MessageContextType.TASK,
        task_id=offer_task.id,
        source=source
    )
    request.state.session.add(message)
    request.state.session.add(contract)
    request.state.session.commit()
    return {'ok': 'You accepted offer.', 'task': TaskGetSchema.model_validate(offer_task)}


@router.post('/{offer_id}/complaint')
async def complaint_offer(request: Request, token: str, offer: Annotated[dict, Depends(offer_parameter)], complaint_type: str):
    """
    Soon...
    \f
    :param token: Токен для авторизации
    :param request:
    :param offer:
    :param complaint_type:
    :return:
    """
    pass