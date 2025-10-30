import datetime

from typing import List
from pydantic import BaseModel, Field, ConfigDict

from api.routers.tasks.client_tasks.schemas import TaskGetSchema
from api.routers.users.freelancer.schemas import FreelancerSchema

from db.models import OfferStatusType, JuridicalType, PaymentType


class OfferFreelancerSchema(FreelancerSchema):
    has_windows_client: bool
    completed_tasks_count: int
    days_in_service: int
    juridical_type: JuridicalType | None = None
    payment_types: List[PaymentType] = []


class GetOffersSchema(BaseModel):
    """
    Схема отклика

    Attributes:
        id (int): айди отклика
        status (OfferStatusType): статус отклика (принят, отказано)
        description (str): описание отклика
        budget (int): бюджет отклика
        deadline_days (int): срок отклика
        author (FreelancerSchema): автор отклика
        task: (TaskGetSchema): заказ на который сделан отклик
        created_at (datetime.datetime): дата создания отклика
        edited_at (datetime.datetime): дата последнего изменения
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: OfferStatusType
    description: str
    budget: int | None
    deadline_days: int
    author: OfferFreelancerSchema
    task: TaskGetSchema
    created_at: datetime.datetime | None
    edited_at: datetime.datetime | None = Field(alias='updated_at')
