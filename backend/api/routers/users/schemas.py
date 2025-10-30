from pydantic import BaseModel, ConfigDict
from db.models import (
    CountryType,
    JuridicalType,
    PaymentType,
    RoleType,
    ProfessionalLevelType,
    NotificationType
)
from typing import List
from datetime import datetime


class MinimumUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str | None
    full_name: str
    bio: str | None
    phone: str | None
    skills: List[str] | None
    created_at: datetime | None
    registered_at: datetime | None


class UserSchema(BaseModel):
    id: int
    telegram_id: int
    username: str | None
    full_name: str
    reff_telegram_id: int | None
    bio: str | None
    phone: str | None
    roles: List[RoleType]
    country: CountryType | None
    juridical_type: JuridicalType | None
    payment_types: List[PaymentType]
    prof_level: ProfessionalLevelType | None
    skills: List[str] | None
    is_registered: bool
    notification_types: List[NotificationType]
    free_task_period: datetime | None
    banned_until: datetime | None
    registered_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None
