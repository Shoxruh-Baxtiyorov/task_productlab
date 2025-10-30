import datetime
from typing import Annotated, List
import aio_pika
import loader
from api.routers.tasks.freelancer_tasks.dependencies import freelancer_task_parameter
from api.routers.tasks.freelancer_tasks.schemas import MakeOfferSchema, MyOffersSchema, MyContractsSchema
from db.crud import CommonCRUDOperations
from db.models import *
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import and_, or_, func, case
from db.database import SessionLocal
from api.routers.tasks.freelancer_tasks.schemas import PublicTaskSchema

router = APIRouter(tags=['Freelancer tasks'])
# ответ на запрос если не найден заказ
task_not_found = JSONResponse({'error': 'Task not found.'}, status_code=404)


@router.get('', response_model=list[MyContractsSchema])
async def get_my_contracts(request: Request, token: str, offset: int | None = None, limit: int | None = None):
    """
    Получение контрактов фрилансера
    :param request: запрос
    :param token: токен авторизации
    :param offset: оффсет
    :param limit: лимит
    :return: список заказов
    """
    q = request.state.session.query(Contract, Task).join(Task, Contract.task_id == Task.id).filter(
        Contract.freelancer_id == request.state.user.id)
    if offset:
        q = q.offset(offset)
    if limit:
        q = q.limit(limit)

    results = q.all()

    contracts_with_tasks = [
        {**contract.__dict__, "task": task}
        for contract, task in results
    ]
    for item in contracts_with_tasks:
        item.pop('_sa_instance_state', None)

    return contracts_with_tasks


@router.get('/offers', response_model=list[MyOffersSchema])
async def get_my_offers(request: Request, token: str, offset: int | None = None, limit: int | None = None):
    """
    Получение заказов фрилансера
    :param request: запрос
    :param token: токен авторизации
    :param offset: оффсет
    :param limit: лимит
    :return: список заказов
    """
    q = request.state.session.query(Task).filter(Task.freelancer_id == request.state.user.id)
    if offset:
        q = q.offset(offset)
    if limit:
        q = q.limit(limit)
    return q.all()


@router.post('/{task_id}/cancel')
async def cancel_task(request: Request, token: str, task: Annotated[Task, Depends(freelancer_task_parameter)]):
    """
    Отменить текущую задачу фрилансера
    \f
    :param request: запрос
    :param token: токен атворизации
    :param task: заказ
    :return: 404 or 409 or 200
    """
    if not task:
        return task_not_found
    if task.status == TaskStatusType.ATWORK or task.status == TaskStatusType.SUBMITTED:
        contract = request.state.session.query(Contract).where(
            and_(
                Contract.task_id == task.id,
                Contract.status == ContractStatusType.ATWORK
            )
        ).first()
        contract.status = ContractStatusType.CANCELLED
        contract.cancelled_by_freelancer = True
        contract.work_stopped_at = datetime.now()
        task.status = TaskStatusType.CANCELLED
        request.state.session.commit()
        return JSONResponse({'ok': 'You cancelled this task.'})
    else:
        return JSONResponse({'error': f'You can\'t cancel this task. This task has status {task.status.name}'},
                            status_code=409)


@router.post('/{task_id}/offer')
async def make_offer(request: Request, token: str, task_id: int, offer_body: MakeOfferSchema):
    """
    Отправить отклик на заказ
    \f
    :param request: запрос
    :param token: токен атворизации
    :param task_id: айди заказа
    :param offer_body: форма отклика
    :return: 404 or 410 or 403 or 409 or 200
    """
    task = request.state.session.query(Task).get(task_id)
    if not task:
        return task_not_found
    if task.status != TaskStatusType.ACCEPTSOFFERS:
        return JSONResponse({'error': 'This task does not accept offers anymore.'}, status_code=410)
    user_relations = request.state.session.query(UserRelation).filter(
        or_(
            and_(
                UserRelation.user_id == request.state.user.id,
                UserRelation.related_user_id == task.author_id
            ).self_group(),
            and_(
                UserRelation.user_id == task.author_id,
                UserRelation.related_user_id == request.state.user.id
            ).self_group()
        )
    ).first()
    if user_relations and (
            user_relations.status == UserRelationStatusType.BLOCKED or user_relations.status == UserRelationStatusType.DISALLOW_OFFERS):
        return JSONResponse({'error': 'You are not allowed to make offers to this users\' tasks.'}, status_code=403)
    offer = request.state.session.query(Offer).filter(
        and_(Offer.task_id == task.id, Offer.author_id == request.state.user.id)).first()
    if offer:
        return JSONResponse({'error': 'You already made offer to this task.'}, status_code=409)
    offer_body = dict(offer_body)
    offer_body.update(
        author_id=request.state.user.id,
        task_id=task.id,
        status=OfferStatusType.PENDING
    )
    CommonCRUDOperations.create_offer(request.state.session, **offer_body)

    await loader.bot.send_message(
        task.author.telegram_id,
        f'У вас новый отклик на заказ {task.title}\n\n'
        f'Исполнитель: {request.state.user.full_name}\n'
        f'Дата регистрации: {request.state.user.created_at}\n\n'
        f'Отклики по данной задаче: {loader.URL}/offers?token={task.author.token}&task_id={task.id}\n\n'
        f'Отклик по всем задачам: <a href="{loader.URL}/offers?token={task.author.token}">тут</a>\n'
        f'Все ваши задачи: <a href="{loader.URL}/tasks/my?token={task.author.token}">тут</a>\n'
        f'API-документация: <a href="{loader.URL}/docs">тут</a>\n\n'
        f'Ваш токен: <b>{task.author.token}</b>',
        disable_web_page_preview=True
    )
    return JSONResponse({'ok': 'Offer sent.'})


@router.post('/{task_id}/submit')
async def submit_task(request: Request, token: str, task: Annotated[Task, Depends(freelancer_task_parameter)]):
    """
    Сдать работу по заказу на проверку
    \f
    :param request: запрос
    :param token: токен авторизации
    :param task: заказ
    :return: 404 or 200
    """
    if not task:
        return task_not_found
    if task.status == TaskStatusType.ATWORK:
        request.state.session.add(Message(
            author_id=request.state.user.id,
            receiver_id=task.author_id,
            context=MessageContextType.TASK,
            task_id=task.id,
            type=MessageType.SUBMITWORK,
            source=MessageSourceType.WINDOWSCLIENT
        ))
        task.status = TaskStatusType.SUBMITTED
        request.state.session.commit()

        await new_freelancer_message(task)

        return JSONResponse({'ok': 'Work submitted. Client will check and accept your work.'})
    else:
        return JSONResponse({'error': f'You can\'t submit this task. This task has status {task.status.name}'})


@router.get('/available', response_model=List[PublicTaskSchema])
async def get_available_tasks():
    """
    Get all available tasks that are accepting offers
    """
    session = SessionLocal()
    try:
        tasks = (
            session.query(
                Task,
                func.count(Offer.id).label('offers_count'),
                func.count(
                    case(
                        (Offer.status == OfferStatusType.PENDING, 1)
                    )
                ).label('pending_offers_count')
            )
            .join(Task.author)
            .outerjoin(Offer, Task.id == Offer.task_id)
            .filter(
                and_(
                    Task.status == TaskStatusType.ACCEPTSOFFERS,
                    Task.archived == False
                )
            )
            .group_by(Task.id, Task.author_id)
            .all()
        )
        
        return [
            {
                **{
                    k: v for k, v in task[0].__dict__.items() 
                    if not k.startswith('_')
                },
                'author': {
                    'id': task[0].author.id,
                    'username': task[0].author.username,
                    'full_name': task[0].author.full_name,
                    'profile_photo_url': task[0].author.profile_photo_url,
                    'prof_level': task[0].author.prof_level.value if task[0].author.prof_level else None,
                    'country': task[0].author.country.value if task[0].author.country else None
                },
                'offers_count': task[1],
                'pending_offers_count': task[2]
            }
            for task in tasks
        ]
    finally:
        session.close()


async def new_freelancer_message(task):
    """
    Продюсер, отправляющий сообщение в консюмер для новых заказов
    """
    # устанавливаем соединение
    connection = await aio_pika.connect_robust(host=loader.RABBIT_HOST, port=5672, timeout=10)
    async with connection:
        # название очереди, вроде как
        routing_key = 'freelancer_messages'
        # получаем канал
        channel = await connection.channel()
        # публикуем сообщение о новом заказе
        await channel.default_exchange.publish(
            aio_pika.Message(body=str(task.id).encode()),
            routing_key=routing_key
        )