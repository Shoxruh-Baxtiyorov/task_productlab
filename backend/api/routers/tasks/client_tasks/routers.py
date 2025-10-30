import datetime
from datetime import datetime
import json
from json.decoder import JSONDecodeError
from typing import Annotated, Optional

from fastapi import APIRouter, Request, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from api.routers.tasks.client_tasks.dependencies import client_task_parameter
from api.routers.tasks.client_tasks.schemas import *
from db.models import Task, TaskStatusType, TaskAutoResponse
from bot.routers.create_task_router import publish_new_task
from api.validation.models import HardTaskCreate


router = APIRouter(tags=['Client tasks'])

task_not_found_response = JSONResponse({'error': 'Task not found'})


@router.post('')
async def create_my_task(request: Request, token: str, task: TaskCreateSchema):
    task_dict = dict(task)
    task_db = Task(
        author_id=request.state.user.id,
        deadline_days=task.deadline,
        **{d: task_dict[d] for d in task_dict if d != 'deadline'})
    request.state.session.add(task_db)
    request.state.session.commit()
    return JSONResponse(
        {'ok': 'Task created successfully.', 'task': jsonable_encoder(dict(TaskGetSchema.model_validate(task_db)))})


@router.get('/newhardtask')
async def create_hard_task(
        request: Request, 
        token: str,
        title: str,
        description: str,
        tags: str,
        budget_from: int,
        budget_to: int,
        deadline: int,
        reminds: int, 
        private_content: str | None=None,
        all_auto_responses: bool | None=Query(False, description="If you transmit True (autoresponses for everyone), " 
                                              "you are not required to transmit the rules. If you pass False, you must " 
                                              "pass the rules."),
        rules: Optional[str]=Query(None, description="This field can only accept a json string. "
                                            "The rules for autoresponses are passed to this field. "
                                            "If you do not want to transmit the rules, leave this field empty.",
                                example='{"budget_to": 0,'
                                         '"budget_from": 100,'
                                         '"deadline_days": 2,'
                                         '"qty_freelancers": 5}')):
    try:
        rules = json.loads(rules) if rules else None
        task = HardTaskCreate(
                title=title,
                description=description,
                tags=tags,
                budget_from=budget_from,
                budget_to=budget_to,
                deadline_days=deadline,
                private_content=private_content,
                number_of_reminders=reminds,
                all_auto_responses=all_auto_responses,
                rules=rules)
        rules = task.rules
        task = task.model_dump()
        _ = task.pop("rules")
        task_db = Task(
            author_id=request.state.user.id,
            **task,
        )
        request.state.session.add(task_db)
        request.state.session.commit()
        await publish_new_task(task_db)
        if rules:
            task_id = task_db.id
            rules["task_id"] = task_id
            autoresponse = TaskAutoResponse(
                **rules,
            )
            request.state.session.add(autoresponse)
            request.state.session.commit()
        task["rules"] = rules
        return JSONResponse(
        {'ok': 'HardTask created successfully.', 'task': jsonable_encoder(task)})
    except ValidationError as exc:
        return JSONResponse({"error": str(exc)}, status_code=422)
    except JSONDecodeError as exc:
        return JSONResponse({"error": str(exc)}, status_code=422)


@router.get('', response_model=List[TaskGetSchema])
async def my_tasks(
        request: Request,
        token: str,
        tags: str | None = None,
        archived: bool | None = False,
        offset: int | None = None,
        limit: int | None = None):
    """
    Получить мои задачи
    \f
    :param token: Токен для авторизации
    :param request: Запрос пользователя
    :param tags: необязательные теги для фильтрации
    :param archived: необязательный параметр, по умолчанию false
    :param offset: оффсет
    :param limit: лимит результата
    :return: список заказов
    """
    q = request.state.session.query(Task).filter(Task.author_id == request.state.user.id)
    if tags:
        q = q.filter(Task.tags.contains([tags.split(',')]))
    if not archived:
        q = q.filter(Task.archived.is_(False))
    if limit:
        q = q.limit(limit)
    if offset:
        q = q.offset(offset)
    return q.all()


@router.post('/{task_id}/accept')
async def accept_work(request: Request, token: str, task: Annotated[Task, Depends(client_task_parameter)]):
    if not task:
        return task_not_found_response
    if task.status == TaskStatusType.SUBMITTED:
        task.status = TaskStatusType.COMPLETED
        task.contract.work_stopped_at = datetime.now()
        task.contract.status = ContractStatusType.COMPLETED
        request.state.session.commit()
        return JSONResponse({'ok': 'Work accepted, task is completed!'})
    return JSONResponse({'error': f'Freelancer did not submit work. Current task status: {task.status.value}'})


@router.post('/{task_id}/archive')
async def archive_task(request: Request, token: str, task: Annotated[Task, Depends(client_task_parameter)]):
    """
    Архивировать заказ
    \f
    :param token: Токен для авторизации
    :param request: Запрос пользователя
    :param task: заказ
    :return: 200 or 404
    """
    if not task:
        return task_not_found_response
    task.archived = True
    task.status = TaskStatusType.ARCHIVED
    request.state.session.commit()
    return JSONResponse({'ok': 'Task archived'})


@router.post('/{task_id}/cancel')
async def cancel_task(request: Request, token: str, task: Annotated[Task, Depends(client_task_parameter)]):
    """
    Отмена заказа заказчиком
    :param request: запрос
    :param token: токен атворизации
    :param task: объект заказа
    :return: 409 или 200
    """
    if not task:
        return task_not_found_response
    if task.status == TaskStatusType.ATWORK or task.status == TaskStatusType.SUBMITTED:
        contract = request.state.session.query(Contract).where(
            and_(
                Contract.freelancer_id == task.freelancer_id,
                Contract.task_id == task.id,
                Contract.status == ContractStatusType.ATWORK
            )
        ).first()
        contract.status = ContractStatusType.CANCELLED
        contract.work_stopped_at = datetime.now()
        task.status = TaskStatusType.CANCELLED
        request.state.session.commit()
        return {'ok': 'You cancelled this task.'}
    return JSONResponse({'error': f'You can\'t cancel this task. This task has status {task.status.name}'},
                        status_code=409)


@router.patch('/{task_id}')
async def change_task(request: Request, token: str, task: Annotated[Task, Depends(client_task_parameter)],
                      updated_task: TaskUpdateSchema):
    """
    Изменить данные заказа
    \f
    :param token: Токен для авторизации
    :param request: Запрос пользователя
    :param task: изменяемый заказ
    :param updated_task: Новые параметры заказа
    :return: Обновленный заказ
    """
    if not task:
        return task_not_found_response
    task.update(
        {
            'title': updated_task.title or Task.title,
            'description': updated_task.description or Task.description,
            'budget_from': updated_task.budget_from if updated_task.budget_from and updated_task.budget_to else Task.budget_from,
            'budget_to': updated_task.budget_to if updated_task.budget_from and updated_task.budget_to else Task.budget_to,
            'deadline_days': updated_task.deadline or Task.deadline_days,
            'tags': updated_task.tags or Task.tags
        }
    )
    request.state.session.commit()
    updated_task = {k: v for k, v in dict(updated_task).items() if v is not None}
    updated_task['id'] = task.id
    return {'ok': updated_task}


@router.post('/{task_id}/republish')
async def republish_task(request: Request, token: str, task: Annotated[Task, Depends(client_task_parameter)]):
    if not task:
        return task_not_found_response
    if task.status in [TaskStatusType.ARCHIVED, TaskStatusType.CANCELLED]:
        task.status = TaskStatusType.ACCEPTSOFFERS
        task.contract_id = None
        task.archived = False
        task.freelancer_id = None
        request.state.session.commit()
        return {'ok': 'Task republished.', 'task': TaskGetSchema.model_validate(task)}
    else:
        return JSONResponse({'error': f'Task cannot be republished now. It\'s current status: {task.status}'},
                            status_code=409)
