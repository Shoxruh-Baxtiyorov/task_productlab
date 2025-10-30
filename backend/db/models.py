from typing import Optional

from sqlalchemy import (
    func,
    text,
    Column,
    select,
    BigInteger,
    Float,
    Boolean,
    Integer,
    String,
    Enum,
    DateTime,
    ForeignKey,
    and_,
    case,
    Numeric,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, mapped_column, Mapped, validates
from datetime import datetime

from .database import *

import enum
import uuid


class TaskStatusType(enum.StrEnum):
    ATWORK = "ATWORK"
    ACCEPTSOFFERS = "ACCEPTSOFFERS"
    ARCHIVED = "ARCHIVED"
    SUBMITTED = "SUBMITTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class OfferStatusType(enum.StrEnum):
    SAMPLED = "SAMPLED"
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"


class NotificationType(enum.StrEnum):
    """
    ENUM с типами уведомлений, на который подписан пользователь
    """

    PLATFORM = "PLATFORM"
    NEWTASKS = "NEWTASKS"
    RESPONSES = "RESPONSES"


class RoleType(enum.StrEnum):
    """
    ENUM с ролями, выбранными пользователем
    """

    FREELANCER = "FREELANCER"
    CLIENT = "CLIENT"


class CountryType(enum.StrEnum):
    """
    ENUM со страной пользователя (Россия, не Россия)
    """

    RUSSIA = "RUSSIA"
    NOTRUSSIA = "NOTRUSSIA"


class JuridicalType(enum.StrEnum):
    """
    ENUM с типом лица пользователя
    """

    IP = "IP"
    SELF_EMPLOYED = "SELF_EMPLOYED"
    OOO = "OOO"
    PHYSICAL = "PHYSICAL"


class PaymentType(enum.StrEnum):
    """
    ENUM с типами оплаты, доступными для пользователя
    """

    SBER = "SBER"
    SELF_EMPLOYED = "SELF_EMPLOYED"
    CRYPTO = "CRYPTO"
    NONCASH = "NONCASH"


class ProfessionalLevelType(enum.StrEnum):
    """
    ENUM с проф. уровнем пользователя
    """

    JUNIOR = "JUNIOR"
    MIDDLE = "MIDDLE"
    SENIOR = "SENIOR"


class UserRelationStatusType(enum.StrEnum):
    """
    ENUM с типами статусов отношений между пользователями
    """

    NEUTRAL = "NEUTRAL"
    HIDE_OFFERS = "HIDE_OFFERS"
    DISALLOW_OFFERS = "DISALLOW_OFFERS"
    OFFERSENDED = "OFFERSENDED"
    STARTWORK = "STARTWORK"
    WORKINVITE = "WORKINVITE"
    WORKDONE = "WORKDONE"
    ONECLOSEDPROJECT = "ONECLOSEDPROJECT"
    BLOCKED = "BLOCKED"


class SubscriptionStatusType(enum.StrEnum):
    """
    ENUM с типами статусов подписки (слать, не слать)
    """

    SEND = "SEND"
    DONTSEND = "DONTSEND"


class SubscriptionType(enum.StrEnum):
    """
    ENUM с типами подписок (и, или)
    """

    AND = "AND"
    OR = "OR"


class MessageContextType(enum.StrEnum):
    OFFER = "OFFER"
    TASK = "TASK"


class MessageType(enum.StrEnum):
    ACCEPTOFFER = "ACCEPTOFFER"
    STARTWORK = "STARTWORK"
    SUBMITWORK = "SUBMITWORK"
    WORKACCEPTED = "WORKACCEPTED"
    DEADLINESPENT = "DEADLINESPENT"
    AUTOSCREENS = "AUTOSCREENS"
    MESSAGE = "MESSAGE"


class MessageSourceType(enum.StrEnum):
    WINDOWSCLIENT = "WINDOWSCLIENT"
    BOT = "BOT"
    WEB = "WEB"


class ContractStatusType(enum.StrEnum):
    ATWORK = "ATWORK"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    INSPECTED = "INSPECTED"


class TokenStatus(enum.StrEnum):
    """
    ENUM с типами статусов публичного токена
    """

    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class SkillLevelType(enum.StrEnum):
    """
    ENUM с уровнями навыков пользователя в сегменте
    """

    WANT = "WANT"  # Хочет (0 claimed, 0 completed)
    WILL = "WILL"  # Будет (>0 claimed, <3 completed)
    IN = "IN"      # В теме (>=3 completed)


class UserSegmentReasonType(enum.StrEnum):
    """
    ENUM с причинами добавления сегмента пользователю
    """

    USER_SKILLS = "USER_SKILLS"                      # Из навыков пользователя
    USER_BIO_DESCRIPTIONS = "USER_BIO_DESCRIPTIONS"  # Из описания профиля
    USER_SUBSCRIBED = "USER_SUBSCRIBED"              # Из подписок пользователя
    USER_RESUME = "USER_RESUME"                      # Из резюме пользователя
    TASK_OFFER = "TASK_OFFER"                        # Из отклика на задачу


class SubscriptionReasonType(enum.StrEnum):
    """
    ENUM с причинами создания подписки
    """

    USER_SUBSCRIBED = "USER_SUBSCRIBED"  # Пользователь создал вручную
    USER_RESUME = "USER_RESUME"          # Создана из резюме
    TASK_OFFER = "TASK_OFFER"            # Создана из отклика на задачу


class MutableList(Mutable, list):
    """
    Кастомная модель, делающая массив изменяемым (mutable)
    """

    def append(self, value):
        """
        Добавление элемента в массив

        :param value: значение добавляемого элемента
        :return: None
        """
        list.append(self, value)
        self.changed()

    def remove(self, value):
        """
        Удаления элемента из массива по его значению

        :param value: значение элемента, которого нужно удалить
        :return: None
        """
        list.remove(self, value)
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        """
        Хз что это
        """
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value


class User(Base):
    """
    Модель пользователя

    :param token: токен пользователя для доступа в апи
    :param telegram_id: айди пользователя в телеграм
    :param username: имя пользователя в телеграм
    :param full_name: полное имя пользователя в телеграм
    :param reff_telegram_id: айди реферера в телеграм, если он есть
    :param bio: описание пользователя
    :param phone: номер телефона пользователя
    :param location_latitude: первое число координат геолокации пользователя
    :param location_longitude: второе число координат геолокации пользователя
    :param roles: роли (исполнитель или клиент)
    :param country: страна, из России или не из России
    :param juridical_type: тип лица (юрлицо, физлицо)
    :param payment_types: типы платежей доступные пользователю
    :param prof_level: проф уровень пользователя (джуниор, миддл, сеньеор)
    :param skills: навыки пользователя
    :param notification_types: типы уведомлений на которых подписался пользователь
    :param is_registered: проверка о заполнении пользователем формы
    :param free_task_period: дата до которой пользователь может бесплатно размещать задачи
    :param banned_until: дата до которой пользователь заблокирован в боте
    :param created_at: дата регистрации пользователя в базе
    :param updated_at: дата последнего изменения пользователя
    :param chat_id: идентификатор чата пользователя
    :param profile_photo_url: url фото профиля пользователя из хранилища S3
    :param registration_start_parameter: параметр команды /start при регистрации пользователя
    :param fromme: разрешил ли пользователь создать подписку
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(UUID(as_uuid=True), default=uuid.uuid1)
    telegram_id = Column(BigInteger)
    username = Column(String, nullable=True)
    full_name = Column(String)
    reff_telegram_id = Column(BigInteger, nullable=True)
    bio = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    location_latitude = Column(Float, nullable=True)
    location_longitude = Column(Float, nullable=True)
    roles = Column(
        MutableList.as_mutable(
            ARRAY(Enum(RoleType, create_constraint=False, native_enum=False))
        ),
        default=[],
    )
    country = Column(Enum(CountryType), nullable=True)
    juridical_type = Column(Enum(JuridicalType), nullable=True)
    payment_types = Column(
        MutableList.as_mutable(
            ARRAY(Enum(PaymentType, create_constraint=False, native_enum=False))
        ),
        default=[],
    )
    prof_level = Column(Enum(ProfessionalLevelType), nullable=True)
    skills = Column(MutableList.as_mutable(ARRAY(String)), nullable=True)
    is_registered = Column(Boolean, default=False)
    is_dead = Column(Boolean, default=False)
    has_windows_client = Column(Boolean, default=False)
    notification_types = Column(
        MutableList.as_mutable(
            ARRAY(Enum(NotificationType, create_constraint=False, native_enum=False))
        ),
        default=[],
    )
    free_task_period = Column(DateTime, nullable=True)
    banned_until = Column(DateTime, nullable=True)
    is_blocked = Column(Boolean, default=False)
    registered_at = Column(DateTime, nullable=True)
    owner_id = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    rating = relationship("Rating", uselist=False, back_populates="user")
    rating_history = relationship("RatingHistory", back_populates="user")
    profile_photo_url = Column(String, nullable=True)
    registration_start_parameter = Column(String, nullable=True)
    fromme = Column(Boolean, default=False, nullable=False)

    @hybrid_property
    def completed_tasks_count(self):
        return len(
            [
                t
                for t in self.my_freelancer_tasks
                if t.status == TaskStatusType.COMPLETED
            ]
        )

    @completed_tasks_count.expression
    def completed_tasks_count(cls):
        return (
            select(func.count(Task.id))
            .where(
                and_(
                    Task.freelancer_id == cls.id,
                    Task.status == TaskStatusType.COMPLETED,
                )
            )
            .label("completed_tasks_count")
        )

    @hybrid_property
    def days_in_service(self):
        return (datetime.now() - self.created_at).days

    @days_in_service.expression
    def days_in_service(cls):
        return select([func.datediff(text("day"), datetime.now(), cls.created_at)])

    def __str__(self):
        return f'<User:{self.id} {"@" + self.username if self.username else ""} {self.full_name}>'


class Distribution(Base):
    """
    Таблица с информацией о рассылках
    Attributes:
        id (int): айди рассылки
        author_id (int): автор рассылки
        author (User): объект автора
        roles (list): целевые роли рассылки
        message_chat_id (int): чат сообщения рассылки
        message_id (int): сообщение рассылки
        created_at (datetime): дата создания
        updated_at (datetime): дата последнего изменения
    """

    __tablename__ = "distributions"

    id = Column(Integer, autoincrement=True, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", backref="my_distributions", foreign_keys=[author_id])
    roles = Column(
        MutableList.as_mutable(
            ARRAY(Enum(RoleType, create_constraint=False, native_enum=False))
        ),
        default=[],
    )
    message_chat_id = Column(BigInteger)
    message_id = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)


class Subscription(Base):
    """
    Модель для подписок фрилансеров на определенные категории

    :param user_id: foreign key пользователя
    :param user: пользователь
    :param tags: теги, на которые подписан пользователь
    :param budget_from: минимальный бюджет заказов
    :param budget_to: максимальный бюджет заказов
    :param status: статус подписки (слать, или не слать)
    :param type: тип подписки (и, или)
    :param created_at: дата добавления подписки
    :param updated_at: дата последнего изменения подписки
    :param fromme: разрешил ли пользователь создать подписку
    """

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref="my_subscriptions", foreign_keys=[user_id])
    tags = Column(MutableList.as_mutable(ARRAY(String(50))))
    budget_from = Column(Integer, nullable=True)
    budget_to = Column(Integer, nullable=True)
    status = Column(Enum(SubscriptionStatusType), default=SubscriptionStatusType.SEND)
    type = Column(Enum(SubscriptionType))
    reason_added = Column(Enum(SubscriptionReasonType), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    segments_processed = Column(Boolean, default=False)
    fromme = Column(Boolean, default=False, nullable=False)


class UserRelation(Base):
    """
    Модель для определения статусов отношений между пользователями

    :param user_id: foreign key пользователя
    :param user: пользователь
    :param related_user_id: foreign key второго пользователя, в отношении которого применяется статус
    :param related_user: второй пользователь, в отношении которого применяется статус
    :param status: статус отношений (заблокирован, скрывать предложения etc.)
    :param created_at: дата создания отношений
    :param updated_at: дата последнего изменения отношений
    """

    __tablename__ = "user_relations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref="my_relations", foreign_keys=[user_id])
    related_user_id = Column(Integer, ForeignKey("users.id"))
    related_user = relationship(
        "User", backref="my_relation_relateds", foreign_keys=[related_user_id]
    )
    status = Column(
        Enum(UserRelationStatusType), default=UserRelationStatusType.NEUTRAL
    )
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)


class Offer(Base):
    """
    Модель для откликов от исполнителей

    :param description: описание отклика
    :param status: статус отклика (выбран в выборку, ожидает ответа, отклонен, и т.д.)
    :param budget: бюджет оклика
    :param deadline_days: срок отклика в ЧАСАХ!!!
    :param author_id: foreign key фрилансера который сделал отклик
    :param author: фрилансер который сдал отклик
    :param task_id: foreign key задачи, на которую был сделан отклик
    :param task: задача, на которую был сделан отклик
    :param created_at: дата регистрации пользователя в базе
    :param updated_at: дата последнего изменения пользователя
    """

    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(4096))
    status = Column(Enum(OfferStatusType), default=OfferStatusType.PENDING)
    budget = Column(Integer, nullable=True)
    deadline_days = Column(Integer, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", backref="my_offers", foreign_keys=[author_id])
    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task", backref="offers", foreign_keys=[task_id])
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)


class Task(Base):
    """
    Модель для опубликованных задач и заказов.

    :param status: статус заказа (в работе, отменен)
    :param author_id: foreign key пользователя, разместившего заказ
    :param author: пользователь, разместивший заказ
    :param title: короткое название проекта\n
    :param description: описание задачи
    :param all_auto_responses: определяет, нужно ли автоматически принимать отклики абсолютно всех фрилансеров
    :param budget: бюджет проекта, если указан заказчиком. Если нет, оплата по договору\n
    :param budget_from: минимум бюджета размещенной задачи
    :param budget_to: максимум бюджета размещенной задачи
    :param deadline_days: срок проекта в ЧАСАХ!!!\n
    :param tags: список тегов по задаче\n
    :param freelancer_id: foreign key фрилансерa, который работает над заказом, если он в работе
    :param freelancer: фрилансер, который работает над заказом, если он в работе
    :param archived: определяет, архивирован заказ или нет
    :param work_started_at: дата начала работ по заказу
    :param work_stopped_at: дата завершения заказа
    :param created_at: дата регистрации пользователя в базе
    :param updated_at: дата последнего изменения пользователя
    :param is_lite_offer: быстрый отклик (описание бюджет сроки брать из задачи)

    """

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(Enum(TaskStatusType), default=TaskStatusType.ACCEPTSOFFERS)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", backref="my_tasks", foreign_keys=[author_id])
    title = Column(String(100))
    description = Column(String(5000))
    all_auto_responses = Column(Boolean, default=False)
    budget_from = Column(Integer, nullable=True)
    budget_to = Column(Integer, nullable=True)
    deadline_days = Column(Integer, nullable=True)
    tags = Column(MutableList.as_mutable(ARRAY(String)))
    freelancer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    freelancer = relationship(
        "User", backref="my_freelancer_tasks", foreign_keys=[freelancer_id]
    )
    archived = Column(Boolean, default=False)
    private_content = Column(String(5000), nullable=True)
    number_of_reminders = Column(Integer, nullable=True)
    is_hard = Column(Boolean, nullable=True)
    is_lite_offer = Column(Boolean, nullable=True, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    @property
    def deadline(self):
        if self.status == TaskStatusType.ATWORK:
            for c in self.contracts:
                if c.status == ContractStatusType.ATWORK:
                    return c.deadline_days
        return self.deadline_days

    @property
    def budget(self):
        if self.status == TaskStatusType.ATWORK:
            for c in self.contracts:
                if c.status == ContractStatusType.ATWORK:
                    return c.budget

    @property
    def offers_count(self):
        return len(self.offers)

    @property
    def pending_offers_count(self):
        return len([o for o in self.offers if o.status == OfferStatusType.PENDING])

    @property
    def emoji_status(self):
        """Returns an emoji-based status string showing task statistics"""
        working = len(
            [c for c in self.contracts if c.status == ContractStatusType.ATWORK]
        )
        rejected = len([o for o in self.offers if o.status == OfferStatusType.REJECTED])
        completed = len(
            [c for c in self.contracts if c.status == ContractStatusType.COMPLETED]
        )

        status = []
        if working > 0:
            status.append(f"В работе👨‍💻 {working}")
        if rejected > 0:
            status.append(f"Отказались❌ {rejected}")
        if completed > 0:
            status.append(f"Выполнили✅ {completed}")

        return " ".join(status) if status else "🆕"


class MessageFile(Base):
    __tablename__ = "message_files"

    id = Column(Integer, autoincrement=True, primary_key=True)
    key = Column(String)
    bucket_name = Column(String, default="deadlinetaskbot-default-bucket")
    path = Column(String)
    message_id = Column(Integer, ForeignKey("messages.id"))
    message = relationship("Message", backref="attachments", foreign_keys=[message_id])
    is_uploaded = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)


class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", backref="my_messages", foreign_keys=[author_id])
    receiver_id = Column(Integer, ForeignKey("users.id"))
    receiver = relationship(
        "User", backref="my_received_messages", foreign_keys=[receiver_id]
    )
    context = Column(Enum(MessageContextType))
    source = Column(Enum(MessageSourceType))
    type = Column(Enum(MessageType))
    text = Column(String)
    offer_id = Column(Integer, ForeignKey("offers.id"))
    offer = relationship("Offer", backref="messages", foreign_keys=[offer_id])
    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task", backref="messages", foreign_keys=[task_id])
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)


class Contract(Base):
    """
    Модель для договоров.

    :param freelancer_id: foreign key фрилансера, работающего над заказом
    :param freelancer: фрилансер, работающий над заказом
    :param client_id: foreign key заказчика, работающего над заказом
    :param client: заказчик, работающий над заказом
    :param offer_id: foreign key отклика
    :param offer: отклик
    :param task_id: foreign key задачи
    :param task: задача
    :param budget: бюджет договора
    :param evaluate: оценка исполнителя
    :param comment_freelancer: комментарий фрилансера в договоре
    :param deadline_days: срок договора в ЧАСАХ!!!
    :param deadline_at: дата окончания договора
    :param miss_deadline: флаг пропуска срока договора
    :param status: статус договора
    :param work_started_at: дата начала работ по договору
    :param work_stopped_at: дата завершения договора
    :param cancelled_by_freelancer: флаг отменены договора фрилансером
    """

    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    freelancer_id = Column(Integer, ForeignKey("users.id"))
    freelancer = relationship(
        "User", backref="my_freelancer_contracts", foreign_keys=[freelancer_id]
    )
    client_id = Column(Integer, ForeignKey("users.id"))
    client = relationship(
        "User", backref="my_client_contracts", foreign_keys=[client_id]
    )
    offer_id = Column(Integer, ForeignKey("offers.id"))
    offer = relationship("Offer", backref="contract", foreign_keys=[offer_id])
    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task", backref="contracts", foreign_keys=[task_id])
    budget = Column(Integer)
    evaluate = Column(Integer, nullable=True)
    comment_freelancer = Column(String(5000), default=False)
    deadline_days = Column(Integer, nullable=True)
    deadline_at = Column(DateTime, nullable=True)
    miss_deadline = Column(Boolean, default=False)
    status = Column(Enum(ContractStatusType), default=ContractStatusType.ATWORK)
    work_started_at = Column(DateTime, nullable=True)
    work_stopped_at = Column(DateTime, nullable=True)
    cancelled_by_freelancer = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    segments_processed = Column(Boolean, default=False)


class SchedulerTask(Base):
    __tablename__ = "scheduler_tasks"

    id = Column(Integer, primary_key=True)
    object_id = Column(Integer, nullable=False)
    task_name = Column(String, nullable=False)
    deadline_date = Column(DateTime, nullable=False)
    job_id = Column(String, nullable=True)
    method_name = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)
    interval_hours = Column(Float, default=0.0)
    last_message_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class PublicToken(Base):
    """Модель для сохранения публичных токенов"""

    __tablename__ = "public_token"

    token: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    owner_id = mapped_column(ForeignKey("users.id"))
    owner = relationship("User", backref="my_tokens", foreign_keys=[owner_id])
    status: Mapped[TokenStatus] = mapped_column(default=TokenStatus.ACTIVE)
    title: Mapped[Optional[str]] = mapped_column(String(100), default="Без названия")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.now)


class Rating(Base):
    """
    Модель для рейтинга пользователей.

    :param user_id: foreign key пользователя, чей рейтинг отслеживается
    :param user: пользователь, чей рейтинг отслеживается
    :param score: рейтинг
    :param created_at: дата создания объекта рейтинга в базе
    :param updated_at: дата последнего изменения объекта рейтинга
    """

    __tablename__ = "rating"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    user = relationship("User", back_populates="rating")
    score = Column(Numeric(10, 1), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    @validates("score")
    def validate_score(self, key, score):
        if score < 0:
            raise ValueError("Score must be positive")
        return score


class RaitingChangeDirection(enum.StrEnum):
    PLUS = "+"
    MINUS = "-"


class RatingHistory(Base):
    """
    Модель для истории изменений рейтинга пользователей.

    :param user_id: foreign key пользователь, у которого изменяется рейтинг
    :param user: пользователь
    :param change_direction: направление изменения рейтинга + или -
    :param score: соличество очков на сколько изменился рейтинг
    :comment: коментарий к изменению рейтинга
    :param created_at: дата создания объекта изменения рейтинга
    """

    __tablename__ = "rating_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", back_populates="rating_history")

    change_direction = Column(
        Enum(RaitingChangeDirection), default=RaitingChangeDirection.PLUS
    )
    score = Column(Numeric(10, 1), nullable=False)
    comment = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    @validates("score")
    def validate_score(self, key, score):
        if score < 0:
            raise ValueError("Score must be positive")
        return score


class TaskAutoResponse(Base):
    """
    Модель для данных автоматического приема откликов.

    :param budget_from: минимум бюджета размещенной задачи, default=0
    :param budget_to: максимум бюджета размещенной задачи, default=100000
    :param deadline_days: максимальный срок выполнения проекта в ЧАСАХ!!!, default=100
    :param qty_freelancers: количество исполнителей, default=1
    :param created_at: дата создния в базе
    """

    __tablename__ = "auto_responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task", backref="auto_responses", foreign_keys=[task_id])
    budget_from = Column(Integer, default=0)
    budget_to = Column(Integer, default=100000)
    deadline_days = Column(Integer, default=100)
    qty_freelancers = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    def __repr__(self):
        return (
            f"<TaskAutoResponse(task_id={self.task_id}, budget_from={self.budget_from}, budget_to={self.budget_to}, "
            f"deadline_days={self.deadline_days}, qty_freelancers={self.qty_freelancers})>"
        )


class Segment(Base):
    __tablename__ = "segments"

    id = Column(Integer, primary_key=True)
    name = Column(String(128))


class UserSegment(Base):
    __tablename__ = "user_segments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref="segments", foreign_keys=[user_id])
    segment_id = Column(Integer, ForeignKey("segments.id"))
    segment = relationship("Segment", backref="users", foreign_keys=[segment_id])
    claimed_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    skill_level = Column(Enum(SkillLevelType), nullable=True)
    reason_added = Column(Enum(UserSegmentReasonType), nullable=True)
    fromme = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    
class LoyaltyPoints(Base):
    """
    Model for storing loyalty points

    :param user_id: ID of user who received points (freelancer)
    :param client_id: ID of user who awarded points (client)
    :param amount: Number of points awarded
    :param expires_at: When points expire
    :param is_used: Whether points have been used
    :param notification_count: How many notifications to send
    :param notifications_sent: How many notifications have been sent
    :param created_at: When points were awarded
    """

    __tablename__ = "loyalty_points"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="loyalty_points", foreign_keys=[user_id])
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client = relationship(
        "User", backref="awarded_loyalty_points", foreign_keys=[client_id]
    )
    amount = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    notification_count = Column(Integer, nullable=False)
    notifications_sent = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)


class Resume(Base):
    """
    Модель для хранения резюме пользователей

    :param user_id: ID пользователя
    :param file_url: URL файла резюме в S3
    :param file_type: Тип файла (pdf, doc, etc)
    :param raw_text: Сырой текст из резюме
    :param source: Источник резюме (hh.ru, linkedin, etc)
    :param is_active: Активно ли резюме
    """

    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref="resumes")
    file_url = Column(String)
    file_type = Column(String)
    raw_text = Column(String)
    source = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
