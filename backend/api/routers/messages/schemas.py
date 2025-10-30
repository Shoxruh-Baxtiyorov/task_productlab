from pydantic import BaseModel, ConfigDict, Json
from typing import List

from api.routers.users.schemas import MinimumUserSchema
from api.routers.offers.client_offers.schemas import GetOffersSchema
from api.routers.tasks.client_tasks.schemas import TaskGetSchema

from db.models import *


class MessageFileSchema(BaseModel):
    """
    Схема для возвращения JSON объекта файла события
    \f
    Attributes:
        id (int): айди файла
        key (str): ключ файла в хранилище S3
        bucket_name (str): название бакета
        path (str): название файла
        is_uploaded (bool): загружен или нет
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    bucket_name: str
    path: str
    is_uploaded: bool


class CreateMessageSchema(BaseModel):
    receiver_id: int
    context: MessageContextType
    source: MessageSourceType | None
    type: MessageType
    text: str | None = None
    offer_id: int | None = None
    task_id: int | None = None


class GetMessageIdSchema(BaseModel):
    id: int
    author_id: int


class GetMessageSchema(CreateMessageSchema, GetMessageIdSchema):
    model_config = ConfigDict(from_attributes=True)

    interlocutor_id: int
    interlocutor: MinimumUserSchema
    offer: GetOffersSchema | None
    task: TaskGetSchema | None
    attachments: List[MessageFileSchema] = []
    created_at: datetime
