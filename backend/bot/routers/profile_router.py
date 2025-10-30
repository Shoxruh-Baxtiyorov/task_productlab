from aiogram import Router, filters, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext


from sqlalchemy.orm import Session

from bot.keyboards import profile_keyboards as kb
from bot.keyboards.start_keyboards import send_phone_number_keyboard
from bot.states.profile_states import TokenStates
from bot.states.start_states import Registration

from db.models import *

import loader

r = Router()


@r.message(filters.Command('publictoken'), StateFilter(None))
async def get_public_token(msg: types.Message, state: FSMContext,  db_session: Session, user: User):
    """
    Создание или получение публичного токена
    :param msg: сообщение
    :param user: пользователь в БД
    """
    token: Optional[PublicToken] = db_session.query(PublicToken).filter(and_(
        PublicToken.owner == user,
        PublicToken.status == TokenStatus.ACTIVE)).first()
    if not token:
        await state.set_state(TokenStates.title)
        return await msg.answer('Введите название(описание) публичного токена:')

    await msg.answer("\n".join([
        'Ваш публичный токен для передачи заказчикам:',
        f'Название: "{token.title}"',
        f'Токен: <code>{token.token}</code>'
    ]))


@r.message(TokenStates.title)
async def set_public_token(msg: types.Message, state: FSMContext,  db_session: Session, user: User):
    title = msg.text[:50]
    token = PublicToken(owner=user, title=title)
    db_session.add(token)
    db_session.commit()
    await state.clear()

    await msg.answer("\n".join([
        'Ваш публичный токен для передачи заказчикам:',
        f'Название: "{token.title}"',
        f'Токен: <code>{token.token}</code>'
    ]))


@r.message(filters.Command('token'))
async def get_token(msg, user):
    """
    Получение токена
    :param msg: сообщение
    :param user: пользователь в БД
    """
    await msg.answer(
        f'Ваш токен: <code>{user.token}</code>'
    )


@r.message(filters.Command('referral'))
async def get_referral(msg):
    """
    Команда для получения собственной реферальной ссылки
    :param msg: объект сообщения
    """
    await msg.answer(
        f'Ваша уникальная ссылка для приглашения в телеграм-бота: {loader.BOT_ADDRESS}?start=ref{msg.from_user.id}\n\n'
        f'С каждого исполнителя и заказчика вы будете получать бонусы на платформе!'
    )


async def get_push(event):
    """
    Метод для запуска режима настройки оповещений
    :param event: событие (сообщение, колбек)
    """
    await event.bot.send_message(
        event.from_user.id,
        'Вы запустили режим перенастройки оповещений',
        reply_markup=kb.push_keyboard()
    )


@r.callback_query(F.data == 'push_menu')
async def get_push_callback(cb):
    """
    Запуск режима настройки оповещений с коллбека
    :param cb: коллбек
    """
    await get_push(cb)
    await cb.message.delete()


@r.message(filters.Command('push'))
async def get_push_message(msg):
    """
    Запуск режима настройки оповещений с команды
    :param msg: сообщение
    """
    if msg.chat.type == 'private':
        await get_push(msg)


@r.message(filters.Command('settings'))
async def get_settings(msg, user: User):
    """
    Просмотр профиля. Предлагает перезаполнить данные.
    :param msg: объект сообщения
    :param user: пользователь в БД
    """
    if msg.chat.type == 'private':
        await msg.answer(
            f'<b>{user.full_name}</b>\n\n'
            f'Роль: <b>{", ".join([role.value for role in user.roles])}</b>\n'
            f'Номер: <b>{user.phone}</b>\n'
            f'Из России: <b>{"да" if user.country == CountryType.RUSSIA else "нет"}</b>\n'
            f'Юридический статус: <b>{user.juridical_type.value if user.juridical_type.value else "Отсутствует"}</b>\n'
            f'Проф. уровень: <b>{user.prof_level.value}</b>\n'
            f'Навыки: <b>{", ".join(user.skills)}</b>\n'
            f'О себе: <b>{user.bio}</b>',
            reply_markup=kb.settings_keyboard()
        )


@r.callback_query(F.data == 'restart_register')
async def get_register_restart(cb, state):
    """
    Реагирует на коллбек перезаполнения
    :param cb: коллбек
    :param state: состояние
    """
    await state.set_state(Registration.phone)
    await cb.message.edit_reply_markup(None)
    await cb.bot.send_message(
        cb.from_user.id,
        'Отправьте ваш номер телефона через кнопку снизу:',
        reply_markup=send_phone_number_keyboard()
    )
