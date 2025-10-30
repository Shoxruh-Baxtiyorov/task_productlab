from pydantic import BaseModel, ConfigDict
from typing import List

from db.models import *

from api.routers.users.freelancer.schemas import FreelancerSchema


class TaskCreateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    budget_from: int | None = None
    budget_to: int | None = None
    deadline: int | None = None
    tags: List[str] | None = None


class TaskUpdateSchema(BaseModel):
    """
    Форма для обновления заказа
    Attributes:
        title (str | None): новое название заказа
        description (str | None): новое описание заказа
        budget_from (int | None): новый минимум бюджета
        budget_to (int | None): новый максимум бюджета
        deadline_days (int | None): новый срок заказа
        tags (List[str] | None): новые теги заказа
    """
    title: str | None = None
    description: str | None = None
    budget_from: int | None = None
    budget_to: int | None = None
    deadline: int | None = None
    tags: List[str] | None = None


class TaskGetSchema(TaskUpdateSchema):
    """
    Схема для получения заказа
    Attributes:
        status (TaskStatusType): статус заказа (в работе, принимает отклики)
        author_id (int): автор заказа
        freelancer (FreelancerSchema | None): фрилансер, который работает над заказом, если он в работе
        archived (bool): архивирован или нет
        work_started_at (datetime | None): дата начала работ по заказу
        work_stopped_at (datetime | None): дата окончания заказа
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: TaskStatusType
    author_id: int
    budget: int | None = None
    freelancer: FreelancerSchema | None
    archived: bool
    offers_count: int
    pending_offers_count: int
    created_at: datetime | None
    updated_at: datetime | None
