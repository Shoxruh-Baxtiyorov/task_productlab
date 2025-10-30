from aiogram import Router, F, filters, types
from sqlalchemy import and_

from bot.middlewares.admin_middleware import AdminMiddleware
from bot.states.admin_states import MassiveMessagingState
from bot.keyboards import admin_keyboards as kb
from db.models import *

import loader
import datetime
import aio_pika

r = Router()
r.message.middleware(AdminMiddleware(loader.ADMINS))
r.callback_query.middleware(AdminMiddleware(loader.ADMINS))


@r.message(filters.Command('stat'))
async def get_stat(msg, db_session):
    """
    Вызывается командой /stat, дает общую статистику по БД бота
    :param msg: объект сообщения
    :param db_session: сессия БД
    """
    await msg.answer('Получаю инфу из БД...')
    today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    # all users count
    all_users_count = db_session.query(User).count()

    # freelancers count
    freelancers_count = db_session.query(User).filter(
        User.roles.contains([RoleType.FREELANCER])).count()

    # clients count
    clients_count = db_session.query(User).filter(
        User.roles.contains([RoleType.CLIENT])).count()

    # dead users count (who blocked bot)
    dead_count = db_session.query(User).filter(
        User.is_dead == True).count()

    # not registered users count
    not_registered_count = db_session.query(User).filter(
        User.is_registered != True).count()

    # users who registered today count
    today_registered_count = db_session.query(User).filter(
        and_(
            User.registered_at < today + datetime.timedelta(days=1),
            User.registered_at >= today
        )
    ).count()

    # users who did not finish register today
    today_not_registered_count = db_session.query(User).filter(
        and_(
            User.is_registered != True,
            and_(
                User.created_at < today + datetime.timedelta(days=1),
                User.created_at >= today
            ).self_group()
        )).count()

    # all tasks count
    all_tasks_count = db_session.query(Task).count()

    # tasks for today count
    today_tasks_count = db_session.query(Task).filter(
        and_(
            Task.created_at < today + datetime.timedelta(days=1),
            Task.created_at >= today
        )
    ).count()

    # send result
    await msg.answer(
        f'<b>Всего пользователей:</b> {all_users_count}\n'
        f'<b>Исполнителей:</b> {freelancers_count}\n'
        f'<b>Заказчиков:</b> {clients_count}\n'
        f'<b>Мертвые души:</b> {dead_count}\n'
        f'<b>Недорегов:</b> {not_registered_count}\n'
        f'<b>Сегодня полных:</b> {today_registered_count}\n'
        f'<b>Сегодня недорегов:</b> {today_not_registered_count}\n'
        f'----------------------------------\n'
        f'Задач всего: <b>{all_tasks_count}</b>\n'
        f'Задач за сегодня: <b>{today_tasks_count}</b>'
    )


@r.message(filters.Command('send'))
async def send_handler(msg, state, user):
    """
    Реагирует на команду /send. Начинает рассылку
    :param msg: объект сообщения
    :param state: состояние
    :param user: пользователь в БД
    """
    await state.update_data(roles=[], author_id=user.id)
    await state.set_state(MassiveMessagingState.roles)
    await msg.answer(
        'Выберите роли, по которым нужно запустить рассылку.',
        reply_markup=kb.distribution_choose_role([])
    )


@r.callback_query(MassiveMessagingState.roles)
async def get_roles(cb, state):
    """
    Выбор нескольких ролей. После выбора предлагает отправить само сообщение
    :param cb: объект колбека
    :param state: состояние
    """
    data = await state.get_data()
    if cb.data == 'next':
        if not data['roles']:
            await cb.answer('⚠️Выберите хотя бы одну роль')
            return
        await state.set_state(MassiveMessagingState.message)
        await cb.bot.send_message(
            cb.from_user.id,
            'Отправьте сообщение рассылки. Вы можете прикрепить фото или видео (только одно), а так же сделать разметку текста'
        )
        await cb.message.delete()
    else:
        if RoleType[cb.data] in data['roles']:
            data['roles'].remove(RoleType[cb.data])
        else:
            data['roles'].append(RoleType[cb.data])
        await state.update_data(roles=data['roles'])
        await cb.message.edit_reply_markup(reply_markup=kb.distribution_choose_role(data['roles']))


@r.message(MassiveMessagingState.message)
async def get_massive_message(msg: types.Message, state):
    """
    Получает сообщение для рассылки и предлагает подтвердить или отменить
    :param msg: объект сообшения
    :param state: состояние
    :return:
    """
    await state.update_data(message_id=msg.message_id, message_chat_id=msg.from_user.id)
    await state.set_state(MassiveMessagingState.confirm)
    await msg.answer('Сообщение получено. Отправить?', reply_markup=kb.confirm())


@r.callback_query(MassiveMessagingState.confirm)
async def get_confirmation(cb, state, db_session):
    """
    Получает подтверждение или отмену
    :param cb: объект колбека
    :param state: состояние
    :param db_session: сессия БД
    """
    if cb.data == 'cancel':
        await cb.bot.send_message(
            cb.from_user.id,
            'Сброшено.'
        )
    else:
        await cb.bot.send_message(cb.from_user.id, 'Начинаю рассылку...')

        # создаем экземпляр рассылки в базе
        data = await state.get_data()
        distribution = Distribution(**data)
        db_session.add(distribution)
        db_session.commit()

        # устанавливаем соединение
        connection = await aio_pika.connect_robust(host=loader.RABBIT_HOST, port=5672, timeout=10)
        async with connection:
            # получаем канал
            channel = await connection.channel()
            # публикуем сообщение о новом заказе
            await channel.default_exchange.publish(
                aio_pika.Message(body=str(distribution.id).encode()),
                routing_key='new_distribution_started'
            )
        await cb.bot.send_message(
            cb.from_user.id,
            'Рассылка начата. Мы уведомим вас об ее окончании.'
        )
    await state.clear()
    await cb.message.delete()


@r.message(filters.Command('myusers'))
async def myusers_handler(msg: types.Message, db_session):
    """
    Обрабатывает команду /myusers, возвращает список пользователей с кнопками для сортировки
    :param msg: объект сообщения
    :param db_session: сессия БД
    """
    users = db_session.query(User).order_by(User.created_at.desc()).limit(30).all()
    users_text = "\n".join(
        [f"{user.full_name or 'N/A'} / @{user.username or 'N/A'} / "
         f"{user.phone or 'N/A'} / {user.completed_tasks_count} / {user.days_in_service} дней"
         for user in users])

    await msg.answer(
        f"Последние пользователи:\n{users_text}",
        reply_markup=kb.user_sorting_options()
    )


@r.callback_query(F.data.startswith('sort_by'))
async def sort_users_handler(cb: types.CallbackQuery, db_session):
    """
    Обрабатывает колбэки сортировки пользователей
    :param cb: объект колбэка
    :param db_session: сессия БД
    """
    sort_type = cb.data.split('__')[1]
    if sort_type == 'date':
        users = db_session.query(User).order_by(User.created_at.desc()).limit(30).all()
    else:  # sort_type == 'tasks'
        users = db_session.query(User).order_by(User.completed_tasks_count.desc()).limit(30).all()

    users_text = "\n".join(
        [f"{user.full_name or 'N/A'} / @{user.username or 'N/A'} / {user.phone or 'N/A'} / {user.completed_tasks_count} / {user.days_in_service} дней"
         for user in users])

    await cb.message.edit_text(
        f"Сортировка по {'дате' if sort_type == 'date' else 'количеству задач'}:\n{users_text}",
        reply_markup=kb.user_sorting_options()
    )
    await cb.answer()
