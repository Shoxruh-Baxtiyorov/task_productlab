import asyncio
from aiogram import Bot
from sqlalchemy.orm import Session
from datetime import datetime

from db.crud import CommonCRUDOperations as crud
from db.models import TaskStatusType, OfferStatusType
from db.database import SessionLocal
from bot.functions.send_message_safely import send_message_safely
from bot.keyboards.task_offer_keyboards import task_offer_return


async def archive_task(bot):
	with SessionLocal() as session:
		tasks = crud.get_tasks_by_status(
			session=session,
			status=TaskStatusType.ACCEPTSOFFERS
		)

		if not tasks:
			return None

		for task in tasks:
			active_offers = crud.get_offers_by_task_id(
				session=session,
				task_id=task.id)
			active_contracts = crud.get_contracts_by_task_id(
				session=session,
				task_id=task.id)

			task_days_delta = datetime.now() - task.created_at

			if abs(task_days_delta.days) > 3:
				if (
					not active_offers or
					(abs(task_days_delta.days) > 30 and not active_contracts) or
					(active_offers and (abs(task_days_delta.days) > 30 and not active_contracts))
				):
					task.archived = True
					task.status = TaskStatusType.ARCHIVED
					session.add(task)
					session.commit()
					author_telegram_id = crud.get_user_by_id(session=session, user_id=task.author_id).telegram_id
					await send_msg_to_rollback(bot, task, author_telegram_id)
					await asyncio.sleep(1)
					continue


async def send_msg_to_rollback(bot, task, chat_id):
	task_archived_days_delta = datetime.now() - task.created_at
	if abs(task_archived_days_delta.days) < 7:
		await send_message_safely(
			bot=bot,
			chat_id=chat_id,
			text=f"Ваша задача \"{task.title}\"\nот {datetime.strftime(task.created_at, '%d-%m-%Y')} ушла в архив из-за:"
				+ "\n\n- отсутствия откликов в течение 3-х дней,"
				+ "\n- не подписания договора в течение 30-ти дней",
			reply_markup=task_offer_return(task))


def unarchive_task(session: Session, task_id: int):
	task = crud.get_task_by_id(
		session=session, task_id=task_id)

	task.status = TaskStatusType.ACCEPTSOFFERS
	task.archived = False
	task.freelancer_id = None
	session.add(task)
	session.commit()