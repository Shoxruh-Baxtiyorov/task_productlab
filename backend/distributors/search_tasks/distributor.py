from datetime import datetime, timedelta

from db.models import *
from bot.utils.deadline_utils import deadline_converted_output
from bot.keyboards.new_task_keyboards import new_task
from distributors.common_filters import filter_task_notif_by_relations

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

import asyncio
import loader


async def filter_relations(sub, tasks_query, session: Session):
    return [task for task in tasks_query.distinct() if filter_task_notif_by_relations(task, sub, session)]


async def filter_budget(sub, tasks_query):
    return tasks_query.filter(or_(
        Task.budget_from == None,
        and_(
            Task.budget_to >= sub.budget_from, sub.budget_to >= Task.budget_from
        )
    ))


async def filter_tags(sub, tasks_query):
    if sub.type == SubscriptionType.AND:
        return tasks_query.filter(Task.tags.contains([sub.tags]))
    return tasks_query.filter(or_(*[Task.tags.contains([t]) for t in sub.tags]))


async def send_tasks(subscription, session):
    # фильтруем заказы, которые принимают отклики
    filtered = session.query(Task).filter(and_(Task.status == TaskStatusType.ACCEPTSOFFERS, Task.created_at >= (datetime.now() - timedelta(days=1))))
    # фильтрация на теги
    filtered = await filter_tags(subscription, filtered)
    # фильтрация на бюджеt
    if subscription.budget_from:
        filtered = await filter_budget(subscription, filtered)
    # еще раз фильтруем на предмет блока со стороны подписчиком заказчика
    final_tasks = await filter_relations(subscription, filtered, session)
    if not final_tasks:
        # если заказов нема, уведомляем об этом
        await loader.bot.send_message(
            subscription.user.telegram_id,
            'На данный момент нет заказов, подходящих вашей подписке.'
        )
    else:
        # если есть, отправляем пользователю все найденные заказы
        message_text = f"""<b>По вашим подпискам опубликован новый заказ!</b>\n
<b>Разместил:</b> %AUTHOR%\n
<b>Заголовок:</b> %TITLE%\n
<b>Описание:</b> %DESCRIPTION%\n
<b>Бюджета:</b> %BUDGET%\n
<b>Срок в днях:</b> %DEADLINE%\n
<b>Теги</b>: %TAGS%"""
        for task in final_tasks:
            await loader.bot.send_message(
                subscription.user.telegram_id,
                message_text.replace(
                    '%AUTHOR%',
                    task.author.full_name + (" @" + task.author.username if task.author.username else "")
                ).replace(
                    '%TITLE%',
                    task.title
                ).replace(
                    '%DESCRIPTION%',
                    task.description
                ).replace(
                    '%BUDGET%',
                    str(task.budget_from) + " - " + str(task.budget_to) + "₽" if task.budget_from else "по договору"
                ).replace(
                    '%DEADLINE%',
                    deadline_converted_output(str(task.deadline_days))
                ).replace(
                    '%TAGS%',
                    ', '.join(task.tags)
                ),
                reply_markup=new_task(task, subscription)
            )
            await asyncio.sleep(1)
    session.close()
