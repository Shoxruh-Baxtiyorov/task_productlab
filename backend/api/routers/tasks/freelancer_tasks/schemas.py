from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from db.models import OfferStatusType, TaskStatusType
from api.routers.users.freelancer.schemas import FreelancerSchema


class MyOffersSchema(BaseModel):
    id: int
    status: TaskStatusType
    author: FreelancerSchema
    title: str
    description: Optional[str] = None
    budget: int | None
    budget_from: int | None
    budget_to: int | None
    deadline: int | None
    tags: List[str]
    archived: bool | None
    created_at: datetime | None
    updated_at: datetime | None


class MyContractsSchema(BaseModel):
    id: int
    freelancer_id: int | None
    client_id: int
    offer_id: int | None
    task_id: int
    budget: int | None
    deadline_days: int | None
    cancelled_by_freelancer: bool | None
    status: TaskStatusType
    work_started_at: Optional[datetime] = None
    work_stopped_at: Optional[datetime] = None
    created_at: datetime | None
    updated_at: datetime | None
    task: MyOffersSchema


class MakeOfferSchema(BaseModel):
    """
    Форма заполнения отклика
    \f
    Attributes:
        description (str): описание отклика
        budget (int): бюджет отклика
        deadline_days (int): срок отклика
    """
    description: str
    budget: int
    deadline_days: int


class TaskAuthorSchema(BaseModel):
    id: int
    username: Optional[str] = None
    full_name: str
    profile_photo_url: Optional[str] = None
    prof_level: Optional[str] = None
    country: Optional[str] = None

    class Config:
        from_attributes = True


class PublicTaskSchema(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    budget_from: Optional[int] = None
    budget_to: Optional[int] = None
    deadline_days: Optional[int] = None
    tags: List[str] = []
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: TaskAuthorSchema
    offers_count: int
    pending_offers_count: int

    class Config:
        from_attributes = True 