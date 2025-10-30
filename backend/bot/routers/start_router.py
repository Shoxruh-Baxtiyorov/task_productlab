import logging
import loader
from datetime import datetime, timedelta
from html import escape

from aiogram import Router, F, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from sqlalchemy.orm.session import Session

from bot.utils.deadline_utils import deadline_converted_output
from bot.keyboards.rating_service_keyboards import info_rating_keyboard
from bot.services.s3_services import S3Services
from bot.constants.rating import *
from bot.keyboards.start_keyboards import *
from bot.states.start_states import *
from bot.services.rating_services import RatingService
from bot.routers.subscribe_router import set_subscription
from db.models import *
from db.crud import CommonCRUDOperations as crud

from bot.services.services_manager import service_manager

r = Router(name="start_router")


@r.callback_query(F.data == "continue")
async def continue_handler(
    cb: types.CallbackQuery, state: FSMContext, db_session: Session, user: User
):
    """
    Обработчик продолжения после любых действий

    :param cb: Объект callback-запроса от Telegram
    :param state: Контекст машины состояний (Finite State Machine)
    :param db_session: Сессия для работы с базой данных SQLAlchemy
    :param user: Пользователь из базы данных
    """
    try:
        # Получаем последнюю команду пользователя
        data = await state.get_data()
        last_command = data.get("last_command")
        logging.info(f"Last command for user {user.telegram_id}: {last_command}")
        if not user.is_registered:
            logging.info(f"Starting registration for user {user.telegram_id}")
            # Если пользователь не зарегистрирован, начинаем регистрацию
            await state.set_state(Registration.phone)
            await cb.message.answer(
                "Добро пожаловать в Deadline bot! Для продолжения вам нужно зарегистрироваться.\n"
                "Для регистрации отправьте ваш номер телефона.",
                reply_markup=send_phone_number_keyboard(),
            )
        elif last_command:
            await cb.message.answer(f"Выполняю команду: {last_command}")
            if last_command == "/start":
                logging.debug("Redirecting to start_handler")
                await start_handler(cb.message, state, db_session, user)
        else:
            logging.debug(
                f"No last command found for user {user.telegram_id}, showing main menu"
            )
            await cb.message.answer("Главное меню")

        logging.info(
            f"Successfully processed continue request for user {user.telegram_id}"
        )

    except Exception as e:
        logging.error(
            f"Error in continue handler for user {user.telegram_id}: {str(e)}",
            exc_info=True,
        )
        await cb.answer("Произошла ошибка, попробуйте позже", show_alert=True)


async def continue_registration(msg: types.Message, state: FSMContext, user: User):
    if user.skills:
        await state.set_state(Registration.bio)
        message = await msg.answer(
            "Выберите оповещения, которые будут приходить из системы:",
            reply_markup=choose_notification_type(user.notification_types),
        )
        return await state.update_data(
            last_message={"text": message.text, "reply_markup": message.reply_markup}
        )

    if user.prof_level:
        await state.set_state(Registration.skills)
        message = await msg.answer(
            "А теперь пришлите через запятую навыки, которыми вы владеете👇",
            reply_markup=None,
        )
        return await state.update_data(
            last_message={"text": message.text, "reply_markup": message.reply_markup}
        )

    if user.payment_types:
        await state.set_state(Registration.prof_level)
        message = await msg.answer(
            "Ваш уровень компетенций по вашему мнению?",
            reply_markup=choose_prof_level(),
        )
        return await state.update_data(
            last_message={"text": message.text, "reply_markup": message.reply_markup}
        )

    if user.juridical_type:
        await state.set_state(Registration.payment_types)
        message = await msg.answer(
            "Какие виды оплат вам доступны?",
            reply_markup=choose_payment_types(user.payment_types),
        )
        return await state.update_data(
            last_message={"text": message.text, "reply_markup": message.reply_markup}
        )

    if user.country:
        await state.set_state(Registration.juridical_type)
        message = await msg.answer(
            "Выберите свой юридический статус:", reply_markup=choose_juridical_type()
        )
        return await state.update_data(
            last_message={"text": message.text, "reply_markup": message.reply_markup}
        )

    if user.roles:
        await state.set_state(Registration.country)
        message = await msg.answer("Вы из России?", reply_markup=choose_country())
        return await state.update_data(
            last_message={"text": message.text, "reply_markup": message.reply_markup}
        )

    if user.phone:
        await state.set_state(Registration.role)
        message = await msg.answer(
            "Ваш номер записан.", reply_markup=types.ReplyKeyboardRemove()
        )
        await state.update_data(
            last_message={"text": message.text, "reply_markup": message.reply_markup}
        )
        message = await msg.answer(
            "Вы успешно зарегистрированы. Пожалуйста, выберите базовую информацию о себе:",
            reply_markup=choose_role_keyboard(user.roles),
        )
        return await state.update_data(
            last_message={"text": message.text, "reply_markup": message.reply_markup}
        )

    return None


@r.message(Command("hello_world_123"))
async def hello_world_test_handler(msg: types.Message):
    """
    Тестовая команда для проверки zero-downtime deployment
    """
    await msg.answer("Hello World! 🚀 Zero downtime deployment works!")


@r.message(F.text.startswith("/start"))
async def start_handler(
    msg: types.Message, state: FSMContext, db_session: Session, user: User
):
    """
    Приветствие и запрос телефона номера для регистрации. Если юзер уже в системе, просто главное меню.
    Если юзер в системе, но не заполнил свои данные (is_registered = False), предлагаем заполнить.
    """

    if user.telegram_id < 0:
        return await msg.answer('Главное меню')

    if msg.text == '/start continue':
        if user or not user.is_registered:
            return await continue_registration(msg=msg, state=state, user=user)

    await state.clear()
    if "task" in msg.text:
        try:
            task_id = int(msg.text.replace("/start task", ""))
            task = db_session.query(Task).filter(Task.id == task_id).first()

            if task:
                formatted_text = (
                    f'<b>Количество уведомлений</b>: {task.number_of_reminders or "Не указано"}\n\n'
                    if task.number_of_reminders and task.number_of_reminders > 0
                    else ""
                )

                await msg.answer(
                    f"<b>Задача</b>:  {task.title}\n\n"
                    f'<b>Разместил:</b> {task.author.full_name + (" @" + task.author.username if task.author.username else "")}\n\n'
                    f"<b>Заголовок:</b> {escape(task.title)}\n\n"
                    f'<b>Описание:</b> {escape(task.description) if task.description else "Это быстрая задача"}\n\n'
                    f"<b>Бюджет</b>: {str(task.budget_from) + ' - ' + str(task.budget_to) + ' руб.' if task.budget_from else 'по договору'}\n\n"
                    f"<b>Срок</b>: {deadline_converted_output(task.deadline_days)}\n"
                    f'<b>Тип задачи:</b> {"Сложная задача, вам будут приходить уведомления о дедлайне." if task.is_hard else "Обычная задача"}\n'
                    f"{formatted_text}"
                    f"<b>Теги</b>: {', '.join(task.tags)}\n",
                    reply_markup=open_task(task),
                )

                return  # Выходим из функции, чтобы не показывать стандартное меню

        except ValueError:
            await msg.answer("❌ Ошибка: неверный формат ссылки.")
    elif not user or not user.bio:
        await state.update_data(open_task=None)
        if not user:
            user = User(
                telegram_id=msg.from_user.id,
                username=msg.from_user.username,
                full_name=msg.from_user.full_name,
            )
            photos = await msg.from_user.get_profile_photos()
            # проверяем, есть ли фото в профиле пользователя
            if photos.photos:
                photo_id = photos.photos[0][-1].file_id
                file_info = await msg.bot.get_file(photo_id)
                file = await msg.bot.download_file(file_info.file_path)
                object_name = "profile-photo." + file_info.file_path.split(".")[-1]
                # сохраняем фото профиля в S3 хранилище
                s3_client = S3Services()  # Больше не передаем bucket_name
                user.profile_photo_url = await s3_client.upload_file(
                    object_name=object_name,
                    file=file,
                    user_id=msg.from_user.id,  # Передаем ID пользователя
                )
            db_session.add(user)
        if "ref" in msg.text:  # проверяем, есть ли в команде старт айди реферера
            try:
                ref_id = int(msg.text.replace("/start ref", ""))
                # проверяем, существует ли он в базе
                ref = db_session.query(User).filter(User.telegram_id == ref_id).first()
                # если существует, добавляем его айди в reff_telegram_id юзера и продлеваем ему бесплатный период
                if ref:
                    user.reff_telegram_id = ref.telegram_id
                    if ref.free_task_period:
                        ref.free_task_period = max(
                            ref.free_task_period + timedelta(days=5),
                            datetime.now() + timedelta(days=5),
                        )
                    else:
                        ref.free_task_period = datetime.now() + timedelta(days=5)
            except ValueError:
                pass
        elif "task" in msg.text:
            try:
                task_id = int(msg.text.replace("/start task", ""))
                task = db_session.query(Task).filter(Task.id == task_id).first()
                if task:
                    await state.update_data(open_task=task.id)
            except ValueError:
                pass
        # добавляем минимальные данные юзера в базу
        db_session.commit()
        # состояние в ожидании номера
        await state.set_state(Registration.role)
        message = await msg.answer(
            'Добро пожаловать в Deadline bot! Для продолжения вам нужно зарегистрироваться.\n'
            'Для регистрации выберите базовую информацию о себе.',
            reply_markup=choose_role_keyboard(user.roles)
        )
    else:
        await msg.answer("Главное меню")


@r.message(Registration.phone, F.contact)
async def get_phone(
    msg: types.Message, state: FSMContext, db_session: Session, user: User
):
    """Получение номера телефона и переход к выбору роли"""
    user.phone = msg.contact.phone_number
    db_session.commit()
    await state.set_state(Registration.notifications)
    message = await msg.answer('Ваш номер записан.', reply_markup=types.ReplyKeyboardRemove())
    await state.update_data(last_message={'text': message.text, 'reply_markup': message.reply_markup})
    message = await msg.answer(
        'Выберите оповещения который будут приходить от системы:',
        reply_markup=choose_notification_type(user.notification_types)
    )


@r.message(
    Registration.phone,
)
async def handle_unselected_phone(msg: types.Message, state: FSMContext):
    """
    Обработчик сообщений, который отвечает пользователю сообщением о необходимости выбора варианта из предложенных кнопок,
    если пользователь пытается отправить сообщение, не выбрав вариант.
    """
    data = await state.get_data()
    last_message = data.get("last_message")
    if last_message:
        await msg.answer(
            "Пожалуйста, отправьте ваш номер телефона, используя кнопку ниже."
        )
        await msg.answer(
            last_message["text"], reply_markup=last_message["reply_markup"]
        )


@r.callback_query(Registration.role)
async def get_role(
    cb: types.CallbackQuery, state: FSMContext, db_session: Session, user: User
):
    """Выбор ролей. Если нажали далее, переходим далее (выбор страны).
    Если нажали другую кнопку, значит выбрали роль или отменили выбор"""
    if cb.data == "next":
        if not user.roles:
            await cb.answer("⚠️Выберите хотя бы одну роль")
            return
        await state.set_state(Registration.country)
        message = await cb.message.edit_text(
            "Вы из России?", reply_markup=choose_country()
        )
        await state.update_data(
            last_message={"text": message.text, "reply_markup": message.reply_markup}
        )
    else:
        if RoleType[cb.data] in user.roles:
            user.roles.remove(RoleType[cb.data])
        else:
            user.roles.append(RoleType[cb.data])
        db_session.commit()
        await cb.message.edit_reply_markup(
            reply_markup=choose_role_keyboard(user.roles)
        )


@r.callback_query(Registration.country)
async def get_country(
    cb: types.CallbackQuery, state: FSMContext, db_session: Session, user: User
):
    """Получение страны (из РФ или нет), предложение выбрать юр статус"""
    user.country = CountryType[cb.data]
    db_session.commit()
    await state.set_state(Registration.juridical_type)
    message = await cb.message.edit_text(
        "Выберите свой юридический статус:", reply_markup=choose_juridical_type()
    )
    await state.update_data(
        last_message={"text": message.text, "reply_markup": message.reply_markup}
    )


@r.callback_query(Registration.juridical_type)
async def get_juridical_type(
    cb: types.CallbackQuery, state: FSMContext, db_session: Session, user: User
):
    """Получение юр.статуса и выбор среди оплат. Так же как и при выборе ролей"""
    user.juridical_type = JuridicalType[cb.data]
    db_session.commit()
    await state.set_state(Registration.payment_types)
    message = await cb.message.edit_text(
        "Какие виды оплат вам доступны?",
        reply_markup=choose_payment_types(user.payment_types),
    )
    await state.update_data(
        last_message={"text": message.text, "reply_markup": message.reply_markup}
    )


@r.callback_query(Registration.payment_types)
async def get_payments(
    cb: types.CallbackQuery, state: FSMContext, db_session: Session, user: User
):
    """Закрепление способов оплаты и предложение выбрать проф. уровень"""
    if cb.data == "next":
        if not user.payment_types:
            await cb.answer("⚠️Выберите хотя бы один способ оплаты")
            return
        await state.set_state(Registration.prof_level)
        message = await cb.message.edit_text(
            "Ваш уровень компетенций по вашему мнению?",
            reply_markup=choose_prof_level(),
        )
        await state.update_data(
            last_message={"text": message.text, "reply_markup": message.reply_markup}
        )
    else:
        if PaymentType[cb.data] in user.payment_types:
            user.payment_types.remove(PaymentType[cb.data])
        else:
            user.payment_types.append(PaymentType[cb.data])
        db_session.commit()
        await cb.message.edit_reply_markup(
            reply_markup=choose_payment_types(user.payment_types)
        )


@r.callback_query(Registration.prof_level)
async def get_prof_level(
    cb: types.CallbackQuery, state: FSMContext, db_session: Session, user: User
):
    """Получение проф. уровня и предложение отправить список навыков"""
    user.prof_level = ProfessionalLevelType[cb.data]
    db_session.commit()
    await state.set_state(Registration.skills)
    message = await cb.message.edit_text(
        "А теперь пришлите через запятую навыки, которыми вы владеете👇",
        reply_markup=None,
    )
    await state.update_data(
        last_message={"text": message.text, "reply_markup": message.reply_markup}
    )


@r.message(Registration.skills)
async def get_skills(
    msg: types.Message, state: FSMContext, db_session: Session, user: User
):
    """Получение списка навыков и предложение дать описание"""
    skills = [skill.replace(" ", "") for skill in msg.text.split(",")]
    user.skills = skills
    db_session.commit()
    await state.set_state(Registration.bio)
    message = await msg.answer(
        "Пришлите описание о себе из любого сервиса или напишите с нуля👇"
    )
    await state.update_data(
        last_message={"text": message.text, "reply_markup": message.reply_markup}
    )


@r.message(Registration.bio)
async def get_bio(
    msg: types.Message, state: FSMContext, db_session: Session, user: User
):
    """Получение описания и предложение выбрать тип уведомлений"""
    user.bio = msg.text
    db_session.commit()
    await state.set_state(Registration.phone)
    message = await msg.answer(
        f'''Готово. Для подтверждения что вы не бот,отправьте свой телефон по кнопке ниже.
        \n<b>Внимание, не присылайте свой телефон в формате цифр, работает только по кнопке</b>:''',
        reply_markup=send_phone_number_keyboard()
    )


async def new_user_notification(bot, user):
    """
    Уведомление админов о новом пользователе
    :param bot: инстанс бота
    :param user: пользователь
    """
    try:    

        if not loader.ADMINS:
            logging.warning("Список ADMINS пуст!")
            return
            
        bio_text = user.bio

        for admin in loader.ADMINS:
            try:
                await bot.send_message(
                    admin,
                    f'Новый пользователь в базе: <b>{user.full_name}</b>\n'
                    f'Адрес: <b>{user.username}</b>\n'
                    f'ID Telegram: <b>{user.telegram_id}</b>\n'
                    f'ID в базе: <b>{user.id}</b>\n'
                    f'Краткое описание: <i>{bio_text[0:401]}</i>'
                )
                logging.info(f"Send notification per {user.username} for {admin}")
            except TelegramBadRequest as e:
                logging.error(f"error sending to admin {admin}: {e}")
            except Exception as e:
                logging.error(f"Unknown error with admin {admin}: {e}")
    
    except Exception as e:
        logging.error(f"Critical error in new_user_notification: {e}")


@r.callback_query(Registration.notifications)
async def get_notifications(cb: CallbackQuery, state: FSMContext, db_session, user, service_manager):
    """Получение типов уведомлений (такой же множественный выбор как при выборе ролей и оплат).
    Последний этап регистрации после которого уже функционал бота"""
    if cb.data == "next":
        if not user.notification_types:
            await cb.answer("⚠️Выберите хотя бы один способ оповещения")
            return
        await cb.message.delete()
        if user.is_registered:
            # если пользователь не новичок а просто перезаполняет профиль
            await cb.bot.send_message(cb.from_user.id, "Ваш профиль успешно заполнен.")
            await state.clear()
        else:
            # если новичок, отмечаем что уже зареган
            await new_user_notification(cb.bot, user)
            user.is_registered = True
            user.registered_at = datetime.now()
            user_rating = (
                db_session.query(Rating).where(Rating.user_id == user.id).one_or_none()
            )
            if not user_rating:
                rating = Rating(
                    user_id=user.id,
                    score=0,
                )
                db_session.add(rating)
            db_session.commit()
            if not user_rating:
                await RatingService.user_rating_change(
                    session=db_session,
                    users_id=user.id,
                    change_direction=RaitingChangeDirection.PLUS,
                    score=REGISRATION_RATING_INCREASE,
                    comment=REGISRATION_RATING_INCREASE_COMMENT,
                )
                await cb.bot.send_message(
                    cb.from_user.id,
                    "Вам начислено 10 баллов за регистрацию.\n",
                    reply_markup=info_rating_keyboard(),
                )

            await service_manager.rating_services.add_weekly_rating_tasks(user.id)
            
            # Добавляем напоминания о загрузке резюме только для фрилансеров
            if RoleType.FREELANCER in user.roles:
                await service_manager.rating_services.add_resume_reminder_tasks(user.id)

            if user.reff_telegram_id:
                ref = (
                    db_session.query(User)
                    .where(User.telegram_id == user.reff_telegram_id)
                    .first()
                )
                if ref:
                    await RatingService.user_rating_change(
                        session=db_session,
                        users_id=ref.id,
                        change_direction=RaitingChangeDirection.PLUS,
                        score=USERS_INVOLVEMENT_RATING_INCREASE,
                        comment=USERS_INVOLVEMENT_RATING_INCREASE_COMMENT,
                    )
                    await cb.bot.send_message(
                        cb.from_user.id,
                        TEXT_RATING_INFO,
                    )
            data = await state.get_data()

            if RoleType.FREELANCER in user.roles:
                await state.clear()
                await cb.bot.send_message(
                    cb.from_user.id,
                    "Что бы в дальнейшем получать уведомления о новых заказах, вам нужно создать подписку. /sub",
                )
            else:
                await state.clear()
                await cb.bot.send_message(
                    cb.from_user.id,
                    "Для создания нового заказа отправьте команду /newtask",
                )

            
            if data['open_task']:
                task = db_session.query(Task).get(data['open_task'])
                await cb.bot.send_message(
                    cb.from_user.id,
                    "Откликнитесь на ваше тестовое задание:",
                )
                message_text = f"<b>Заказ:</b> {task.title}\n\n" \
                               f"<b>Разместил:</b> {task.author.full_name + (' @' + task.author.username if task.author.username else '')}\n" \
                               f"<b>Описание:</b> {task.description}\n" \
                               f"<b>Бюджета:</b> {str(task.budget_from) + ' - ' + str(task.budget_to) + '₽' if task.budget_from else 'по договору'}\n" \
                               f"<b>Срок</b> {deadline_converted_output(task.deadline_days)}\n" \
                               f"<b>Теги</b>: {', '.join(task.tags)}"
                await cb.bot.send_message(cb.from_user.id, message_text, reply_markup=open_task(task))
    else:
        if NotificationType[cb.data] in user.notification_types:
            user.notification_types.remove(NotificationType[cb.data])
        else:
            user.notification_types.append(NotificationType[cb.data])
        db_session.commit()
        await cb.message.edit_reply_markup(
            reply_markup=choose_notification_type(user.notification_types)
        )


@r.message(Registration.role)
@r.message(Registration.country)
@r.message(Registration.juridical_type)
@r.message(Registration.payment_types)
@r.message(Registration.prof_level)
@r.message(Registration.phone, F.contact)
@r.message(Registration.notifications)
async def handle_unselected_message(msg: types.Message, state: FSMContext):
    """
    Обработчик сообщений, который отвечает пользователю сообщением о необходимости выбора варианта из предложенных кнопок,
    если пользователь пытается отправить сообщение, не выбрав вариант.
    """
    data = await state.get_data()
    last_message = data.get("last_message")
    if last_message:
        await msg.answer("Пожалуйста, выберите вариант из предложенных кнопок.")
        await msg.answer(
            last_message["text"], reply_markup=last_message["reply_markup"]
        )


@r.message(Command("myusers"))
async def show_users(
    message: types.Message, state: FSMContext, db_session: Session, user: User
):
    """
    Команда для отображения списка последних 30 исполнителей пользователя
    с возможностью сортировки по разным параметрам
    """
    # Получаем контракты, где текущий пользователь является заказчиком
    contracts = (
        db_session.query(Contract)
        .filter(
            Contract.client_id == user.id,
            Contract.status.in_(
                [ContractStatusType.COMPLETED, ContractStatusType.ATWORK]
            ),
        )
        .order_by(Contract.created_at.desc())
        .all()
    )

    if not contracts:
        await message.answer("У вас пока нет исполнителей.")
        return

    # Собираем уникальных исполнителей
    performers = {}
    for contract in contracts:
        if contract.freelancer_id not in performers:
            freelancer = contract.freelancer

            # Подсчитываем статистику для этого исполнителя
            completed_tasks = (
                db_session.query(Contract)
                .filter(
                    Contract.freelancer_id == freelancer.id,
                    Contract.client_id == user.id,
                    Contract.status == ContractStatusType.COMPLETED,
                )
                .all()
            )

            active_tasks = (
                db_session.query(Contract)
                .filter(
                    Contract.freelancer_id == freelancer.id,
                    Contract.client_id == user.id,
                    Contract.status == ContractStatusType.ATWORK,
                )
                .all()
            )

            completed_sum = sum(c.budget for c in completed_tasks if c.budget)
            active_sum = sum(c.budget for c in active_tasks if c.budget)

            performers[contract.freelancer_id] = {
                "user": freelancer,
                "completed_count": len(completed_tasks),
                "completed_sum": completed_sum,
                "active_count": len(active_tasks),
                "active_sum": active_sum,
                "last_completed": (
                    max([c.created_at for c in completed_tasks])
                    if completed_tasks
                    else None
                ),
            }

    # Берем только последних 30 исполнителей
    performers_list = list(performers.values())[:30]

    # Формируем сообщение
    message_text = "Ваши исполнители:\n\n"
    for p in performers_list:
        freelancer = p["user"]
        message_text += (
            f"👤 {freelancer.full_name}"
            + (f" (@{freelancer.username})" if freelancer.username else "")
            + "\n"
            f"📱 {freelancer.phone if freelancer.phone else 'Телефон не указан'}\n"
            f"✅ Сдано задач: {p['completed_count']} на сумму {p['completed_sum']}₽\n"
            f"⚡️ В работе: {p['active_count']} на сумму {p['active_sum']}₽\n"
            "➖➖➖➖➖➖➖➖➖➖\n"
        )

    # Сохраняем список исполнителей в состояние пользователя
    await state.update_data(performers=performers_list)

    # Отправляем сообщение с кнопками для сортировки
    await message.answer(
        message_text,
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="По дате последних сданных задач",
                        callback_data="sort_performers:date",
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="По количеству сданных задач",
                        callback_data="sort_performers:count",
                    )
                ],
            ]
        ),
    )


@r.callback_query(F.data.startswith("sort_performers:"))
async def sort_performers(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик кнопок сортировки списка исполнителей
    """
    sort_type = callback.data.split(":")[1]

    # Получаем сохраненный список исполнителей
    data = await state.get_data()
    performers_list = data.get("performers", [])

    if not performers_list:
        await callback.answer("Список исполнителей пуст")
        return

    # Сортируем список исполнителей
    if sort_type == "date":
        performers_list.sort(
            key=lambda x: x["last_completed"] if x["last_completed"] else datetime.min,
            reverse=True,
        )
    else:  # sort_type == "count"
        performers_list.sort(key=lambda x: x["completed_count"], reverse=True)

    # Формируем новое сообщение
    new_message_text = "Ваши исполнители:\n\n"
    for p in performers_list:
        freelancer = p["user"]
        new_message_text += (
            f"👤 {freelancer.full_name}"
            + (f" (@{freelancer.username})" if freelancer.username else "")
            + "\n"
            f"📱 {freelancer.phone if freelancer.phone else 'Телефон не указан'}\n"
            f"✅ Сдано задач: {p['completed_count']} на сумму {p['completed_sum']}₽\n"
            f"⚡️ В работе: {p['active_count']} на сумму {p['active_sum']}₽\n"
            "➖➖➖➖➖➖➖➖➖➖\n"
        )

    # Проверяем, изменился ли текст сообщения
    if callback.message.text == new_message_text:
        await callback.answer("Список уже отсортирован таким образом")
        return

    # Обновляем сообщение только если текст изменился
    try:
        await callback.message.edit_text(
            new_message_text,
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="По дате последних сданных задач",
                            callback_data="sort_performers:date",
                        )
                    ],
                    [
                        types.InlineKeyboardButton(
                            text="По количеству сданных задач",
                            callback_data="sort_performers:count",
                        )
                    ],
                ]
            ),
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise

    await callback.answer()


# This is test command for test notifications
# @r.message(Command("testallnotif"))
# async def test_all_notifications(message: Message, user: User):
#     """Тест всех уведомлений разом с интервалом в 2 секунды"""
#     now = datetime.now()
    
#     # Создаем задачи для всех типов уведомлений
#     notifications = [
#         ("first_weekly_rating_advance_notification", "Первое уведомление (через 2 сек)"),
#         ("second_weekly_rating_advance_notification", "Второе уведомление (через 4 сек)"),
#         ("third_weekly_rating_advance_notification", "Третье уведомление (через 6 сек)"),
#         ("fourth_weekly_rating_advance_notification", "Четвертое уведомление (через 8 сек)"),
#         ("fifth_weekly_rating_advance_notification", "Пятое уведомление (через 10 сек)"),
#         ("sixth_weekly_rating_advance_notification", "Шестое уведомление (через 12 сек)"),
#         ("rating_weekly_update", "Уведмоление о списании (через 14 сек)"),
#     ]
    
#     for i, (method_name, description) in enumerate(notifications, 1):
#         test_time = now + timedelta(seconds=i * 2)
        
#         # Получаем метод по имени
#         method = getattr(service_manager.rating_services, method_name)
        
#         await service_manager.scheduler_services.add_job(
#             user.id,
#             description,
#             test_time,
#             method,
#             f"test_{method_name}",
#         )
    
#     await message.answer(
#         "✅ Все тестовые уведомления созданы!\n\n"
#         "📅 Расписание:\n"
#         "• Через 2 сек - Первое уведомление\n"
#         "• Через 4 сек - Второе уведомление\n"  
#         "• Через 6 сек - Третье уведомление\n"
#         "• Через 8 сек - Четвертое уведомление\n"
#         "• Через 10 сек - Пятое уведомление\n"
#         "• Через 12 сек - Шестое уведомление\n"
#         "• Через 14 сек - Еженедельное списание\n\n"
#         "Ждите сообщения! ✅"
#     )
