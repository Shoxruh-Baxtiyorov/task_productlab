import asyncio
import logging
import re
from datetime import datetime, timedelta
from html import escape
from typing import Optional

import aio_pika
import loader

logger = logging.getLogger(__name__)

from aiogram import Router, F, types, Bot, filters
from aiogram.fsm.context import FSMContext
from bot.keyboards.task_offer_keyboards import task_offer_keyboard_for_author, task_offer_apply, task_offer_keyboard_for_freelancer
from bot.keyboards.contract_keyboard import contract_customer_keyboard, contract_executor_keyboard
from bot.keyboards.start_keyboards import choose_role_keyboard, send_phone_number_keyboard
from bot.states.task_offer_states import *
from db.crud import CommonCRUDOperations as crud
from db.models import Message, MessageContextType, MessageSourceType, MessageType, OfferStatusType, \
    TaskStatusType, Contract, User, ContractStatusType, CountryType, PaymentType, JuridicalType

from bot.utils.deadline_utils import deadline_message_validate, str_to_hours_converter, deadline_converted_output
from bot.services.services_manager import service_manager
from bot.states.start_states import Registration
from bot.states.task_offer_states import *
from db.crud import CommonCRUDOperations as crud
from db.models import (Contract, ContractStatusType, CountryType,
                       JuridicalType, Message, MessageContextType,
                       MessageSourceType, MessageType, OfferStatusType,
                       PaymentType, RoleType, Task, TaskStatusType, User,
                       Segment, UserSegment, Subscription, SubscriptionType,
                       SubscriptionStatusType, UserSegmentReasonType,
                       SubscriptionReasonType, SkillLevelType)
from sqlalchemy.orm import Session
from sqlalchemy import func
from bot.services.auto_archiving import unarchive_task


user_services = service_manager.get_user_services()
deadline_services = service_manager.get_deadline_services()
utils_services = service_manager.get_utils_service()
segment_services = service_manager.segment_services
r = Router()

SEARCH_REGEX = r"[a-zA-Z\.\-\#\+]+"


def _calculate_skill_level(claimed_tasks: int, completed_tasks: int) -> SkillLevelType:
    """Вычисляет уровень навыка на основе статистики"""
    if completed_tasks >= 3:
        return SkillLevelType.IN
    elif claimed_tasks > 0 and completed_tasks < 3:
        return SkillLevelType.WILL
    else:
        return SkillLevelType.WANT


def process_offer_segments_and_subscription(db_session: Session, user: User, task: Task):
    """Обрабатывает сегменты и подписку при создании отклика на задачу
    
    Args:
        db_session: Сессия базы данных
        user: Пользователь, который сделал отклик
        task: Задача, на которую был сделан отклик
    """
    try:
        # Extract segments from task
        segment_names = set()
        
        # From task tags
        if task.tags:
            segment_names.update(tag.lower() for tag in task.tags if tag)
        
        # From task description
        if task.description:
            segment_names.update(
                match.group().lower() 
                for match in re.finditer(SEARCH_REGEX, task.description)
            )
        
        if not segment_names:
            return
        
        # Get or create segments
        existing_segments = db_session.query(Segment).filter(
            func.lower(Segment.name).in_(segment_names)
        ).all()
        
        existing_segment_names = {seg.name.lower() for seg in existing_segments}
        segment_name_to_id = {seg.name.lower(): seg.id for seg in existing_segments}
        
        # Create missing segments
        missing_segments = segment_names - existing_segment_names
        if missing_segments:
            new_segments = [Segment(name=name) for name in missing_segments]
            db_session.add_all(new_segments)
            db_session.flush()  # Get IDs for new segments
            
            for seg in new_segments:
                segment_name_to_id[seg.name.lower()] = seg.id
        
        # Process user segments
        existing_user_segments = db_session.query(UserSegment).filter(
            UserSegment.user_id == user.id
        ).all()
        existing_user_segment_ids = {us.segment_id for us in existing_user_segments}
        
        for seg_name, seg_id in segment_name_to_id.items():
            if seg_id not in existing_user_segment_ids:
                # Calculate stats for this segment
                claimed = db_session.query(func.count(Contract.id)).join(Task).filter(
                    Contract.freelancer_id == user.id,
                    Task.description.ilike(f'%{seg_name}%')
                ).scalar() or 0
                
                completed = db_session.query(func.count(Contract.id)).join(Task).filter(
                    Contract.freelancer_id == user.id,
                    Contract.status == ContractStatusType.COMPLETED,
                    Task.description.ilike(f'%{seg_name}%')
                ).scalar() or 0
                
                skill_level = _calculate_skill_level(claimed, completed)
                
                new_user_segment = UserSegment(
                    user_id=user.id,
                    segment_id=seg_id,
                    claimed_tasks=claimed,
                    completed_tasks=completed,
                    skill_level=skill_level,
                    reason_added=UserSegmentReasonType.TASK_OFFER,
                    fromme=False
                )
                db_session.add(new_user_segment)
        
        # Create subscription if it doesn't exist
        tags_list = list(segment_names)
        
        # Check if similar subscription already exists
        existing_subscription = db_session.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.tags.contains(tags_list),
            Subscription.type == SubscriptionType.OR
        ).first()
        
        if not existing_subscription:
            # Check if any subscription with overlapping tags exists
            all_user_subscriptions = db_session.query(Subscription).filter(
                Subscription.user_id == user.id,
                Subscription.status == SubscriptionStatusType.SEND
            ).all()
            
            # Only create if there's no subscription with all these tags
            has_all_tags = False
            for sub in all_user_subscriptions:
                if sub.tags and set(tags_list).issubset(set(tag.lower() for tag in sub.tags)):
                    has_all_tags = True
                    break
            
            if not has_all_tags:
                new_subscription = Subscription(
                    user_id=user.id,
                    tags=tags_list,
                    budget_from=None,
                    budget_to=None,
                    type=SubscriptionType.OR,
                    status=SubscriptionStatusType.SEND,
                    reason_added=SubscriptionReasonType.TASK_OFFER,
                    fromme=False,
                    segments_processed=True
                )
                db_session.add(new_subscription)
                db_session.flush()
                
                # Publish to search tasks queue
                asyncio.create_task(_publish_subscription_async(new_subscription.id))
        
        db_session.commit()
        logger.info(f"Processed segments and subscription for user {user.id} from task {task.id}")
        
    except Exception as e:
        logger.error(f"Error processing offer segments: {e}", exc_info=True)
        db_session.rollback()


async def _publish_subscription_async(subscription_id: int):
    """Публикует сообщение о новой подписке в очередь"""
    try:
        connection = await aio_pika.connect_robust(host=loader.RABBIT_HOST, port=5672, timeout=10)
        async with connection:
            routing_key = 'search_tasks'
            channel = await connection.channel()
            await channel.default_exchange.publish(
                aio_pika.Message(body=str(subscription_id).encode()),
                routing_key=routing_key
            )
    except Exception as e:
        logger.error(f"Failed to publish subscription message: {e}")

@r.callback_query(F.data.startswith('make_offer'))
async def make_offer_handler(cb, state, db_session, user):
    await state.clear()
    # Если пользователь не зарегистрирован – отправляем его в процесс регистрации
    if not await check_registration(cb, state, db_session, user):
        open_task_id = int(cb.data.replace('make_offer:', ''))
        await state.update_data(open_task=open_task_id)
        return # пользователь не зарегистрирован

    task_id = int(cb.data.replace('make_offer:', ''))
    offers = crud.get_offer_by_task_id(session=db_session, task_id=task_id)
    await user_services.unblock_user(user_id=user.id)
    if not user.is_blocked:
        await cb.message.answer('<b>За срыв сроков:</b>\n'
                                'Вам будут заблокированы отклики до сдачи текущей задачи.\n'
                                'После сдачи вы будете заблокированы еще на 7 дней.')

    if user:
        db_session.refresh(user)
        if user.is_blocked:
            block_time = await user_services.block_time(user_id=user.id)
            if user.banned_until:
                return await cb.message.answer(
                    f'Пожалуйста, не срывайте дедлайны на будущих задачах и берите в запас чуть больше времени при отклике.\n\n'
                    f'<b>До конца блокировки осталось: {block_time}</b>\nАпелляция: @natfullin')
            else:
                return await cb.message.answer(
                    f'Вы были заблокированы и не можете больше откликаться пока не сдадите текущую задачу.\n\nАпелляция: @natfullin')
    if not offers or offers.author.telegram_id != user.telegram_id:
        await state.update_data(task_id=task_id)
        await state.set_state(MakeOfferState.description)
        await cb.message.edit_reply_markup(None)
        await cb.message.answer('Напишите описание вашему отклику на проект')
    else:
        await cb.message.answer('Вы уже откликнулись')


@r.message(MakeOfferState.description)
async def get_description(msg, state):
    await state.update_data(description=msg.text)
    await state.set_state(MakeOfferState.budget)
    await msg.answer(
        'Укажите бюджет вашего предложения в рублях. Напишите ЦЕЛОЕ число БЕЗ ПРОБЕЛОВ, ЗАПЯТЫХ И ТОЧЕК.'
    )


@r.message(MakeOfferState.budget)
async def get_budget(msg, state):

    try:
        await state.update_data(budget=int(msg.text))
    except:
        await msg.answer('Неправильный формат. Число должно быть ЦЕЛЫМ, БЕЗ ПРОБЕЛОВ, ЗАПЯТЫХ И ТОЧЕК')
    else:
        await state.set_state(MakeOfferState.deadline)
        await msg.answer('Укажите срок (пример 10д 2ч, 12д, 5ч), в течении которого вы собираетесь сделать проект')


@r.message(MakeOfferState.deadline)
async def get_deadline(msg: types.Message, state, db_session, user):
    msg_validated = deadline_message_validate(msg.text)
    if not msg_validated:
        await msg.answer('Неправильный формат.')
    else:
        await state.update_data(deadline_days=str_to_hours_converter(msg_validated))
        await msg.answer('Создаем и отправляем ваш отклик...')

        data = await state.get_data()
        offer = crud.create_offer(db_session, author_id=user.id, **data)

        # Process segments and subscription from this offer
        process_offer_segments_and_subscription(db_session, user, offer.task)

        # проверяем на автоприем откликов
        if offer.task.all_auto_responses:
            await state.clear()
            return await msg.answer('Ваш отклик будет принят автоматически.',
                             reply_markup=task_offer_keyboard_for_freelancer(offer))


        if offer.task.auto_responses:
            auto_resp = offer.task.auto_responses[0]
            count_contracts = len([c for c in offer.task.contracts])
            if count_contracts < auto_resp.qty_freelancers \
                and auto_resp.budget_from <= offer.budget <= auto_resp.budget_to \
                and auto_resp.deadline_days >= offer.deadline_days:
                await state.clear()
                return await msg.answer('Ваш отклик будет принят автоматически.',
                                 reply_markup=task_offer_keyboard_for_freelancer(offer))

            else:
                await state.clear()
                await msg.answer('⚠️ Ваш отклик не подходит под условия задачи.\nЗаказчик увидит его и примет решение.')


        pfp = await msg.from_user.get_profile_photos(limit=1)

        is_private_chat = msg.chat.type == "private"
        replay_msg = utils_services.get_reply_offer_msg(
            session=db_session,
            user=user,
            offer=offer,
            profile_photo=pfp,
            is_private_chat=is_private_chat
        )

        await msg.bot.send_message(
            offer.task.author.telegram_id,
            replay_msg,
            reply_markup=task_offer_keyboard_for_author(offer),
        )

        await msg.answer('Ваш отклик успешно отправлен.')
        await state.clear()


@r.callback_query(F.data.startswith('lite_make_offer'))
async def make_offer_lite_handler(cb, state, db_session, user):

    await state.clear()

    # Проверка регистрации пользователя
    if not await check_registration(cb, state, db_session, user):
        return # Пользователь не зарегистрирован

    task_id = int(cb.data.replace('lite_make_offer:', ''))
    offers = crud.get_offer_by_task_id(session=db_session, task_id=task_id)
    task = crud.get_task_by_id(session=db_session, task_id=task_id)
    await user_services.unblock_user(user_id=user.id)
    if not user.is_blocked:
        await cb.message.answer('<b>За срыв сроков:</b>\n'
                                'Вам будут заблокированы отклики до сдачи текущей задачи.\n'
                                'После сдачи вы будете заблокированы еще на 7 дней.')

    if user:
        db_session.refresh(user)
        if user.is_blocked:
            block_time = await user_services.block_time(user_id=user.id)
            if user.banned_until:
                return await cb.message.answer(
                    f'Пожалуйста, не срывайте дедлайны на будущих задачах и берите в запас чуть больше времени при отклике.\n\n'
                    f'<b>До конца блокировки осталось: {block_time}</b>\nАпелляция: @natfullin')
            else:
                return await cb.message.answer(
                    f'Вы были заблокированы и не можете больше откликаться пока не сдадите текущую задачу.\n\nАпелляция: @natfullin')
    if not offers or offers.author.telegram_id != user.telegram_id:
        await state.update_data(
            task_id=task_id,
            deadline_days=task.deadline_days,
            description=task.description,
            budget= None if not task.budget_from else task.budget_from
        )
        await cb.message.edit_reply_markup(None)
        bot = cb.message.bot
        await bot.send_message(user.telegram_id, 'Cоздаем и отправляем ваш отклик...')

        data = await state.get_data()
        offer = crud.create_offer(db_session, author_id=user.id, **data)

        # Process segments and subscription from this offer
        process_offer_segments_and_subscription(db_session, user, offer.task)

        pfp = await bot.get_user_profile_photos(user_id=user.telegram_id, limit=1)

        reply_msg = utils_services.get_reply_offer_msg(
            session=db_session,
            user=user,
            offer=offer,
            profile_photo=pfp,
            is_private_chat=True
        )
        if not task.all_auto_responses:
            await bot.send_message(
                offer.task.author.telegram_id,
                reply_msg,
                reply_markup=task_offer_keyboard_for_author(offer),
            )
        else:
            return await cb.message.answer('Ваш отклик будет принят автоматически.',
                             reply_markup=task_offer_keyboard_for_freelancer(offer))


        await bot.send_message(user.telegram_id, 'Ваш отклик успешно отправлен.')
        await state.clear()
    else:
        await cb.message.answer('Вы уже откликнулись')

@r.callback_query(F.data.startswith('apply_offer:'))
async def apply_offer_handler(cb, state, db_session):

    offer_id = int(cb.data.split(':')[1])
    offer = crud.get_offer_by_id(db_session, offer_id=offer_id)

    if offer.status == OfferStatusType.ACCEPTED:
        return await cb.answer("Вы уже отреагировали на этот отклик", show_alert=True)

    status = cb.data.split(':')[2]

    if status == "apply":
        await state.update_data(offer_id=offer_id)
        await cb.message.answer("Пожалуйста введите сумму договора")
        await state.set_state(ApplyOfferState.budget)

    else:

        await cb.message.delete()

    await cb.answer()


@r.message(ApplyOfferState.budget)
async def get_budget(msg, state, db_session, bot):
    try:
        await state.update_data(budget=int(msg.text))
    except:
        return await msg.answer('Неправильный формат. Число должно быть ЦЕЛЫМ, БЕЗ ПРОБЕЛОВ, ЗАПЯТЫХ И ТОЧЕК')
    data = await state.get_data()
    offer = crud.get_offer_by_id(db_session, offer_id=data['offer_id'])
    offer.status = OfferStatusType.ACCEPTED
    offer.budget = data['budget']
    db_session.commit()
    await bot.send_message(
        offer.author.telegram_id,
        "По вашему отклику:\n"
        f"{escape(offer.description)}\n"
        f"На заказ:\n"
        f"{escape(offer.task.title)}\n"
        f"От заказчика:\n"
        f"{offer.task.author.full_name}\n"
        f"Создан новый договор!\n\n"
        f"Согласованная сумма договора. {data['budget']}руб.",
        reply_markup=task_offer_apply(offer)
    )
    await msg.answer("Отправлено исполнителю!")
    await state.clear()


@r.callback_query(F.data.startswith('finish_apply_offer:'))
async def apply_offer_handler(cb, db_session, user, bot, service_manager):
    offer_id = int(cb.data.split(':')[1])
    status = cb.data.split(':')[2]
    if status == "apply" or status == "fast":
        contract = crud.get_contract_by_offer_id(db_session, offer_id=offer_id)
        if contract:
            return await cb.answer("Договор уже создан!", show_alert=True)

        offer = crud.get_offer_by_id(db_session, offer_id=offer_id)
        offer.status = OfferStatusType.ACCEPTED
        offer_task = offer.task
        # остальным откликам по задаче меняем статус на ОТКАЗАНО
        for o in offer_task.offers:
            if o.id != offer.id:
                o.status = OfferStatusType.REJECTED

        # меняем статус задачи на В РАБОТЕ и устанавливаем соответствующие значения
        offer_task.status = TaskStatusType.ATWORK
        offer_task.freelancer_id = offer.author_id

        contract = Contract(
            freelancer_id=offer.author_id,
            client_id=offer_task.author_id,
            offer_id=offer.id,
            task_id=offer_task.id,
            budget=offer.budget,
            deadline_days=offer.deadline_days,
            #измененно на hours, потому что теперь задачи сохраняются в часах.
            deadline_at=datetime.now() + timedelta(hours=offer.deadline_days),
            work_started_at=datetime.now()
        )

        message = Message(
            author_id=user.id,
            receiver_id=offer.author_id,
            type=MessageType.ACCEPTOFFER,
            context=MessageContextType.TASK,
            task_id=offer_task.id,
            source=MessageSourceType.BOT
        )
        db_session.add(contract)
        db_session.add(message)
        db_session.commit()

        await deadline_services.set_deadline(
            contract_id=contract.id,
            task_name='contract',
            deadline_date=contract.deadline_at,
            method_name='trigger_deadline_actions'
        )

        if offer.task.number_of_reminders and offer.task.number_of_reminders > 0:
            await deadline_services.set_deadline_notification(contract_id=contract.id, task_id= offer.task.id, task_name='notification', method_name='deadline_notification_message')

        await service_manager.rating_services.remove_weekly_rating_tasks(user.id)
        await service_manager.rating_services.remove_weekly_rating_tasks(contract.freelancer.id)

        if status == "fast":
                await bot.edit_message_reply_markup(
                    chat_id=cb.message.chat.id,
                    message_id=cb.message.message_id,
                    reply_markup=None
                )
                if offer.task.is_hard:
                    await bot.send_message(
                        contract.freelancer.telegram_id,
                        f"<b>Текущая задача</b>: {escape(contract.task.title)}\n\n"
                        f"<b>Описание задачи</b>: {escape(contract.task.description) if contract.task.description else ''}\n\n"
                        f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n\n"
                        f"Согласованная сумма договора: {contract.budget} руб.",
                        reply_markup=contract_executor_keyboard(contract),
                    )
                    await bot.send_message(
                        contract.freelancer.telegram_id,
                        f"<b>Приватный контент</b>: {offer.task.private_content}\n\n"
                    )
                else:
                    await bot.send_message(
                        contract.freelancer.telegram_id,
                        f"<b>Текущая задача</b>: {escape(contract.task.title)}\n\n"
                        f"<b>Описание задачи</b>: {escape(contract.task.description) if contract.task.description else ''}\n\n"
                        f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n\n"
                        f"Согласованная сумма договора: {contract.budget} руб.",
                        reply_markup=contract_executor_keyboard(contract),
                    )
                await bot.send_message(
                    contract.freelancer.telegram_id,
                    "Ваш договор успешно подписан, приступайте к задаче, как сделаете задачу, нажмите по кнопке сдать работу. Ваша задача уже появилась в вашем windows-приложении как новая задача. Нажмите на запуск в приложении, когда начнете делать задачу.")
                await bot.send_message(
                    offer.task.author.telegram_id,
                    f'<b>Договор подписан</b>: {offer.task.title}\n'
                    f'<b>Исполнитель:</b> {contract.freelancer.full_name} @{contract.freelancer.username}'
                )
        else:
            if offer.task.is_hard:
                await cb.message.edit_text(
                    f"<b>Текущая задача</b>: {escape(contract.task.title)}\n\n"
                    f"<b>Описание задачи</b>: {escape(contract.task.description if contract.task.description else '')}\n\n"
                    f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n\n"
                    f"Согласованная сумма договора: {contract.budget} руб.",
                    reply_markup=contract_executor_keyboard(contract),
                )
                await bot.send_message(
                    contract.freelancer.telegram_id,
                    f"<b>Приватный контент</b>: {offer.task.private_content}\n\n"
                )
            else:
                await cb.message.edit_text(
                    f"<b>Текущая задача</b>: {escape(contract.task.title)}\n\n"
                    f"<b>Описание задачи</b>: {escape(contract.task.description) if contract.task.description else ''}\n\n"
                    f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n\n"
                    f"Согласованная сумма договора: {contract.budget} руб.",
                    reply_markup=contract_executor_keyboard(contract),
                )

            await cb.message.answer(
                "Ваш договор успешно подписан, приступайте к задаче, как сделаете задачу, нажмите по кнопке сдать работу. Ваша задача уже появилась в вашем windows-приложении как новая задача. Нажмите на запуск в приложении, когда начнете делать задачу.")
            await bot.send_message(
                offer.task.author.telegram_id,
                f'<b>Договор подписан</b>: {offer.task.title}\n'
                f'<b>Исполнитель:</b> {contract.freelancer.full_name} @{contract.freelancer.username}'
            )


@r.callback_query(F.data.startswith('return_task:'))
async def return_task_to_cloud(cb, db_session):
    task_id = cb.data.split(':')[1]
    unarchive_task(
        session=db_session,
        task_id=int(task_id))
    await cb.answer()
    await cb.message.delete_reply_markup()
    await cb.message.edit_text("Задача возвращена в облако.\nИсполнитель сброшен")


@r.message(filters.Command('restart'))
async def show_all_waiting_freelancers(msg: types.Message, state: FSMContext, db_session: Session, user: Optional[User]) -> None:
    """Выводим заказчику всех ожидающих исполнителей"""
    try:
        # Проверка зарегистрирован ли пользователь
        await state.clear()

        if not await check_registration(msg, state, db_session, user):
            return # Пользватель не зарегистрирован
        
        # Проверка есть ли пользователь в бд
        user_db = db_session.query(User).filter_by(id=user.id).first()
        if not user_db:
            await msg.answer("Пользователь не найден")
            return 
        
        # Является ли пользователь заказчиком
        if RoleType.CLIENT not in user_db.roles:
            await msg.answer(f"Вы не являетесь заказчиком")
            return 
        
        # Получение всех ожидающих ипсолнителей
        contracts = db_session.query(Contract).filter_by(client_id=user_db.id, status=ContractStatusType.INSPECTED).all()

        if not contracts:
            await msg.answer(f"У вас нет ожидающих исполнителей")
            return

        # Формирование сообщений заказчику
        for idx, contract in enumerate(contracts):
            if idx % 5 == 0 and idx != 0:
                asyncio.sleep(1) # что бы не было флуда обрабатываем пачками по 5

            # Получение очков лояльности
            loyalty_points = crud.get_latest_active_loyalty_points(
                db_session, 
                contract.freelancer_id,
                client_id=contract.task.author_id 
            )
            points_text = f" + {loyalty_points.amount} баллов" if loyalty_points else ""        
            
            text_comment_freelancer = f"Комментарий исполнителя: {contract.comment_freelancer}" if contract.comment_freelancer else ""
    
            time_passed = format_timedelta(contract.updated_at)

            # Отправка оформленного сообщения
            await msg.answer(
                f"<b>Задача выполнена</b>.\n\n"
                f"<b>Название задачи</b>:  {escape(contract.task.title)}\n\n"
                f"<b>Описание задачи</b>:  {escape(contract.task.description) if contract.task.description else ''}\n\n"
                f"Исполнитель: {contract.freelancer.full_name} @{contract.freelancer.username}\n"
                f"Заказчик: {contract.task.author.full_name} @{contract.task.author.username}\n\n"
                f"Согласованная сумма договора: {contract.budget} руб.{points_text}\n\n"
                f'{text_comment_freelancer}\n\n'
                f"Сдано от {time_passed}",
                reply_markup=contract_customer_keyboard(contract)
            )
            
    except Exception as e:
        logging.error(f"Error in show_all_waiting_freelancers: {str(e)}")
        await msg.answer("Произошла ошибка при обработке вашего запроса")

def format_timedelta(updated_time):
    """Формирование времени от которого сдана задача"""

    delta = datetime.now() - updated_time

    days = delta.days
    seconds = delta.seconds 
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    date_part = updated_time.strftime("%d.%m.%Y")
    time_passed = f"{days}д {hours}ч {minutes}м" 

    return f"{date_part} ({time_passed})"


async def check_registration(
        message_or_cb: types.Message | types.CallbackQuery,
        state: FSMContext,
        db_session: Session,
        user: User,
) -> bool:
    """Проверяет завершил ли пользователь регистрацию. Если нет - запускает её."""
    
    if not user:
        user = User(telegram_id=message_or_cb.from_user.id)
        db_session.add(user)
        db_session.commit()

    if user.is_registered:
        return True
    
    if isinstance(message_or_cb, types.CallbackQuery):

        await message_or_cb.message.answer(
        "❗ Для использования этой функции нужно завершить регистрацию.\n\n"
        "📌 Выберите роли ниже:",
        reply_markup=choose_role_keyboard(user.roles)
    )
    else:
        await message_or_cb.answer(
        "❗ Для использования этой функции нужно завершить регистрацию.\n\n"
        "📌 Выберите роли ниже:",
        reply_markup=choose_role_keyboard(user.roles)
        
        )

    await state.set_state(Registration.role)
    return False
