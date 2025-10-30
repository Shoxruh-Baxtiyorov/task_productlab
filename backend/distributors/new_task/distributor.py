from html import escape

from db.models import *
from loader import bot
from bot.utils.deadline_utils import deadline_converted_output
from bot.keyboards.new_task_keyboards import new_task
from distributors.common_filters import filter_task_notif_by_relations
from bot.services.user_services import UserServices

from sqlalchemy import and_, or_
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

import asyncio



async def filter_by_relations(task, subs_query, session):
    return [sub for sub in subs_query.distinct() if filter_task_notif_by_relations(task, sub, session)]


async def filter_tags(task, subs_query):
    return subs_query.filter(
        or_(
            and_(
                Subscription.type == SubscriptionType.AND,
                Subscription.tags.contained_by(task.tags)
            ).self_group(),
            and_(
                Subscription.type == SubscriptionType.OR,
                or_(
                    *[Subscription.tags.contains([t]) for t in task.tags]
                ).self_group()
            ).self_group()
        )
    )


async def filter_budget(task, subs_query):
    if task.budget_from is None:
        return subs_query
    return subs_query.filter(
        or_(
            and_(
                Subscription.budget_from <= task.budget_to,
                Subscription.budget_to >= task.budget_from
            ).self_group(),
            Subscription.budget_from == None
        )
    )


async def send_new_task(task, session):
    # получение подписок со схожими тегами
    subscriptions = session.query(Subscription).filter(Subscription.status == SubscriptionStatusType.SEND)
    subscriptions = await filter_tags(task, subscriptions)
    subscriptions = await filter_budget(task, subscriptions)
    subscriptions = await filter_by_relations(task, subscriptions, session)
    subscriptions = [sub for sub in subscriptions if NotificationType.NEWTASKS in sub.user.notification_types]
    # текст сообщения
    formatted_text = f'<b>Количество уведомлений на весь срок задачи</b>: {task.number_of_reminders or "Не указано"}\n\n' if task.number_of_reminders and task.number_of_reminders > 0 else ''
    sent = set()
    received = set()
    for sub in subscriptions:
        # ну и проходимся по получателям и отправляем сообщения
        if sub.user.id in sent:
            continue
        sent.add(sub.user.id)
        try:
            await bot.send_message(
                sub.user.telegram_id,
                f'<b>По вашим подпискам опубликован новый заказ!</b>\n\n'
                f'<b>Разместил:</b> {task.author.full_name + (" @" + task.author.username if task.author.username else "")}\n\n'
                f'<b>Заголовок:</b> {escape(task.title)}\n\n'
                f'<b>Описание:</b> {escape(task.description) if task.description else "Это быстрая задача"}\n\n'
                f'<b>Бюджета:</b> {str(task.budget_from) + " - " + str(task.budget_to) + "₽" if task.budget_from else "По договору"}\n\n'
                f'<b>Срок:</b> {deadline_converted_output(task.deadline_days) if task.deadline_days else "По договору"}\n'
                f'<b>Тип задачи: </b> {"Сложная задача, вам будут приходить уведомления о дедлайне." if task.is_hard else "Обычная задача"}\n'
                f"{formatted_text}"
                f'<b>Теги</b>: {", ".join(task.tags)}\n',
                reply_markup=new_task(task, sub)
            )
            received.add(sub.user.id)
        except TelegramForbiddenError:
            await UserServices.handle_user_blocked_bot(session, sub.user.id)
        except TelegramBadRequest as e:
            print(f"[{sub.user.telegram_id}]: {e}")

        await asyncio.sleep(1)
    try:
        await bot.send_message(task.author.telegram_id, "\n".join([
            f"Задача была поставлена на рассылку для {len(sent)} подписчиков.",
            f"Успешно удалось отправить рассылку <b>{len(received)}</b> пользователям."]))
    except TelegramForbiddenError:
        await UserServices.handle_user_blocked_bot(session, task.author.id)
    except TelegramBadRequest as e:
        print(f"Создатель задачи {task.author.full_name} ({task.author.telegram_id}): ошибка отправки - {e}")
    session.close()
