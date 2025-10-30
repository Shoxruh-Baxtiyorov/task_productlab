import datetime

from pydantic import BaseModel, ConfigDict
from typing import List


class UpdateFreelancerBioSchema(BaseModel):
    """
    Форма для описания
    """
    new_bio: str


class FreelancerSchema(BaseModel):
    """
    Схема с краткой информацией фрилансера.
    \f
    Attributes:
        id (int): айди фрилансера
        username (str): имя пользователя
        full_name (str): полное имя
        bio (str): описание о себе
        phone (str): номер телефона
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str | None
    full_name: str
    bio: str | None
    phone: str | None
    skills: List[str] | None
    created_at: datetime.datetime | None
    registered_at: datetime.datetime | None
