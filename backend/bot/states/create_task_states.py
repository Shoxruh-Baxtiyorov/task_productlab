from aiogram.fsm.state import State, StatesGroup


class CreateTaskState(StatesGroup):
    """
    Состояния для формы создания заказа
    Attributes:
        title (State): заголовок заказа
        description (State): описание заказа
        tags (State): теги заказа
        auto_responses (State): автоматический прием откликов
        price (State): бюджет заказа
        deadline (State): срок заказа
        confirm (State): подтверждение заказа
        number_of_reminders (State): количество напоминаний для хардтаска
        is_lite_offer (State): быстрый отклик
    """
    title = State()
    description = State()
    tags = State()
    price = State()
    deadline = State()
    number_of_reminders = State()
    lite_tags = State()
    is_lite_offer = State()
    confirm = State()
    private_content = State()


class CreateLiteTaskState(StatesGroup):
    lite_tags = State()
    confirm = State()

class AutoResponseState(StatesGroup):
    """
    Состояния для формы Автоматического приема откликов
    Attributes:
        select (State): выбор автоматического приема откликов
        budget (State): бюджет заказа
        deadline_days (State): срок заказа
        qty_freelancers (State): количество исполнителей
        confirm (State): подтверждение данных

    """
    select = State()
    budget = State()
    deadline_days = State()
    qty_freelancers = State()
    confirm = State()
