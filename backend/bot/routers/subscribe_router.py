from aiogram import Router, F, types
from aiogram.filters import Command

import loader
from bot.states.subscription_states import SubscriptionState
from bot.keyboards.subscription_keyboards import *

from db.models import Subscription, SubscriptionType, SubscriptionStatusType, SubscriptionReasonType

import aio_pika

r = Router(name='subscribe_router')


@r.callback_query(F.data == 'my_subs')
async def get_my_subs(cb, user):
    """
    Получение списка моих подписок
    :param cb: коллбек
    :param user: пользователь в БД
    """
    await cb.message.edit_text(
        'Список ваших подписок:',
        reply_markup=my_subscriptions_list(user.my_subscriptions)
    )


@r.callback_query(F.data.startswith('view_sub:'))
async def view_sub_handler(cb, db_session):
    """
    Интерфейс для отдельной подписки
    :param cb: коллбек
    :param db_session: сессия БД
    """
    sub = db_session.query(Subscription).filter(
        Subscription.id == int(cb.data.replace('view_sub:', ''))).first()
    await cb.message.edit_text(
        f'Теги: <b>{", ".join(sub.tags)}</b>\n'
        f'Тип: <b>{"ИЛИ" if sub.type == SubscriptionType.OR else "И"}</b>\n'
        f'Минимальный бюджет: <b>{"не задан" if not sub.budget_from else str(sub.budget_from) + " ₽"}</b>\n'
        f'Максимальный бюджет: <b>{"не задан" if not sub.budget_to else str(sub.budget_to) + " ₽"}</b>\n'
        f'Статус: <b>{"ВКЛ" if sub.status == SubscriptionStatusType.SEND else "ОТКЛ"}</b>',
        reply_markup=my_subscription_view(sub)
    )


@r.callback_query(F.data.startswith('sub_on_off:'))
async def sub_on_off_handler(cb: types.CallbackQuery, db_session):
    """
    Включить или отключить подписку
    :param cb: коллбек
    :param db_session: сессия БД
    """
    sub = db_session.query(Subscription).filter(
        Subscription.id == int(cb.data.replace('sub_on_off:', ''))).first()
    if sub.status == SubscriptionStatusType.SEND:
        sub.status = SubscriptionStatusType.DONTSEND
        await cb.message.edit_text(
            cb.message.html_text.replace('ВКЛ', 'ОТКЛ'),
            reply_markup=my_subscription_view(sub)
        )
    else:
        sub.status = SubscriptionStatusType.SEND
        await cb.message.edit_text(
            cb.message.html_text.replace('ОТКЛ', 'ВКЛ'),
            reply_markup=my_subscription_view(sub)
        )
    db_session.commit()


@r.callback_query(F.data.startswith('sub_del:'))
async def sub_del_handler(cb, db_session, user):
    """
    Удаление подписки
    :param cb: коллбек
    :param db_session: сессия БД
    :param user: пользователь
    """
    db_session.query(Subscription).filter(
        Subscription.id == int(cb.data.replace('sub_del:', ''))).delete()
    db_session.commit()
    await cb.message.edit_text(
        'Подписка удалена',
        reply_markup=my_subscriptions_list(user.my_subscriptions)
    )


async def set_subscription(event, state):
    """
    Запускает форму для создания подписки
    :param event: событие
    :param state: состояние юзера
    """
    await state.set_state(SubscriptionState.tags)
    await event.bot.send_message(
        event.from_user.id,
        'Давайте настроим вашу первую подписку. Перечислите направления которые вас интересуют, через запятую. '
        'Пример: <b>figma, design, python, fastapi</b>.'
    )


@r.callback_query(F.data == 'add_sub')
async def set_subscription_callback(cb, state):
    """
    Запуск формы для новой подписки с коллбека
    :param cb: коллбек
    :param state: состояние
    """
    await set_subscription(cb, state)
    await cb.message.delete()


@r.message(Command('sub'))
async def set_subscription_command(msg, state):
    """
    Триггер на команду /sub, запускает форму для создания новой подписки.
    """
    await state.clear()
    if msg.chat.type == 'private':
        await set_subscription(msg, state)


@r.message(SubscriptionState.tags)
async def get_tags(msg, state):
    """
    Получение тегов и предложение выбора типа подписки (И, ИЛИ)
    """
    print('debug', msg.from_user.id)
    await state.update_data(tags=[tag.strip().lower() for tag in msg.text.split(',')])
    await state.set_state(SubscriptionState.budget)
    await msg.answer(
        'Напишите бюджет проекта в формате {от}-{до}. Числа должны быть <b>БЕЗ ПРОБЕЛОВ</b>. '
        'Или выберите один из вариантов ниже👇',
        reply_markup=choose_budget()
    )


@r.message(SubscriptionState.budget)
async def get_budget_msg(msg, state):
    """
    Получает бюджет задачи (через ручное написание), запрашивает срок задачи.
    """
    try:
        budget_from = int(msg.text.split('-')[0])
        budget_to = int(msg.text.split('-')[1])
        assert budget_from <= budget_to
    except:
        await msg.answer(
            'Неправильный формат. Бюджет должен указывать в формате {от}-{до}. БЕЗ ПРОБЕЛОВ. Пример:\n\n'
            '55000-90000'
        )
    else:
        await state.set_state(SubscriptionState.subscription_type)
        await msg.answer(
            'Выберите с каким оператором искать для вас задачи.\n\n'
            'Если выбираете <b>И</b>, то в задаче должны обязательно присутствовать все теги, '
            'если <b>ИЛИ</b>, то любой из тегов.',
            reply_markup=choose_subcription_type()
        )


@r.callback_query(SubscriptionState.budget)
async def get_budget_cb(cb, state):
    if cb.data == 'none':
        await state.update_data(budget_from=None, budget_to=None)
    else:
        budget = [int(i) for i in cb.data.split('-')]
        await state.update_data(budget_from=budget[0], budget_to=budget[1])
    await state.set_state(SubscriptionState.subscription_type)
    await cb.message.delete()
    await cb.bot.send_message(
        cb.from_user.id,
        'Выберите с каким оператором искать для вас задачи.\n\n'
        'Если выбираете <b>И</b>, то в задаче должны обязательно присутствовать все теги, '
        'если <b>ИЛИ</b>, то любой из тегов.',
        reply_markup=choose_subcription_type()
    )


@r.callback_query(SubscriptionState.subscription_type)
async def get_subscription_type(cb, state, db_session, user):
    """
    Получаем тип подписки и создаем подписку в базе. Потом отправляем сообщение в консюмер поиска заказов
    """
    # создание экземпляра подписки
    data = await state.get_data()
    subscription = Subscription(
        user_id=user.id,
        type=SubscriptionType[cb.data],
        reason_added=SubscriptionReasonType.USER_SUBSCRIBED,
        **data
    )
    # добавление в базу и коммит
    db_session.add(subscription)
    db_session.commit()
    # очищаем состояние и уведомляем об успешном добавлении
    await state.clear()
    await cb.message.delete()
    await cb.bot.send_message(
        cb.from_user.id,
        'Ваша подписка успешно добавлена. Скоро отправим вам наиболее подходящие заказы.'
    )
    # вызываем продюсер, публикующий сообщение для консюмера по поиску заказов
    await publish_search_task_message(subscription)


@r.callback_query(F.data.startswith('turn_off_sub'))
async def turn_off_sub_handler(cb, db_session, user):
    subscription_id = int(cb.data.replace('turn_off_sub:', ''))
    subscription = db_session.query(Subscription).filter(Subscription.id == subscription_id).first()
    subscription.status = SubscriptionStatusType.DONTSEND
    db_session.commit()
    await cb.message.edit_reply_markup(None)
    await cb.answer('⚠️Теперь данная подписка отключена')


async def publish_search_task_message(subscription):
    """
    Продюсер, отправляющий сообщение о создании подписки и необходимости поиска подходящих заказов
    """
    connection = await aio_pika.connect_robust(host=loader.RABBIT_HOST, port=5672, timeout=10)
    async with connection:
        routing_key = 'search_tasks'
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=str(subscription.id).encode()),
            routing_key=routing_key
        )
        