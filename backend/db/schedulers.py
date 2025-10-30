import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from bot.services.auto_archiving import archive_task


autoarchiving_scheduler = AsyncIOScheduler()

def job_auto_archiving_task(bot):
	try:
		autoarchiving_scheduler.add_job(
			archive_task,
			IntervalTrigger(days=1),
			id="auto_archiving_tasks",
			replace_existing=True,
			misfire_grace_time=30,
			kwargs={"bot": bot})
		autoarchiving_scheduler.start()
		logging.info("Auto-archiving task started")
	except Exception as e:
		logging.error("Canceled by", e)