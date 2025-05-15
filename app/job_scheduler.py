import os
from typing import Callable
from warnings import deprecated
from flask_apscheduler import APScheduler
from apscheduler.jobstores.base import JobLookupError
from flask import Flask
from logging import Logger, getLogger

from app import epd, queue, sleep
from app.consts import *


logger: Logger = getLogger(__name__)
job_scheduler = APScheduler()


@job_scheduler.task("cron", id="update_clock", minute="*", second="2")
def job_update_clock() -> None:
	with job_scheduler.app.app_context():
		sleep_status: SleepStatus = sleep.get_status()
		should_sleep_now: bool = sleep.should_sleep_now()
		logger.debug(f"job_update_clock {sleep_status=} {should_sleep_now=}")

		if should_sleep_now:
			if sleep_status == SleepStatus.AWAKE:
				epd.clear()
				sleep.set_status(SleepStatus.SLEEP)
		else:
			epd.update()
			if sleep_status == SleepStatus.SLEEP:
				sleep.set_status(SleepStatus.AWAKE)


@job_scheduler.task("cron", id="queue_shift_next", hour="*", minute="0", second="1")
def job_queue_shift_next() -> None:
	with job_scheduler.app.app_context():
		queue.shift_next()


def init(app: Flask) -> None:
	global job_scheduler
	if job_scheduler.running or int(os.environ.get("APSC", "1")) == 0:
		logger.warning(f"Scheduler is already running")
		return

	job_scheduler.init_app(app)
	job_scheduler.start()


@deprecated(f"No longer using job scheduler to handle sleep")
def validate_cron_time(day: int, hour: int, minute: int) -> bool:
	if hour < 0 or hour > 23:
		logger.error(f"Invalid hour, {hour=}")
		return False

	if minute < 0 or minute > 59:
		logger.error(f"Invalid minute, {minute=}")
		return False

	if day < 0 or day > 6:
		logger.error(f"Invalid day, {day=}")
		return False

	return True


@deprecated(f"No longer using job scheduler to handle sleep")
def add_cron_job(id: str, func: Callable, day: int, hour: int, minute: int) -> bool:
	logger.info(f"add_cron_job, {id=} {day=} {hour=} {minute=}")

	# Validate cron timing
	validation_result: bool = validate_cron_time(day, hour, minute)
	if not validation_result:
		return False

	global job_scheduler
	job_scheduler.add_job(
		id,
		func,
		trigger="cron",
		replace_existing=True,
		hour=hour,
		minute=minute,
		second="5",
		day_of_week=f"{day}",
	)


@deprecated(f"No longer using job scheduler to handle sleep")
def remove_cron_job(id: str) -> bool:
	global job_scheduler
	try:
		job_scheduler.remove_job(id)
		return True
	except JobLookupError as error:
		logger.error(f"Attempting to remove invalid job id: {id}, {error=}")
		return False


@deprecated(f"No longer using job scheduler to handle sleep")
def get_cron_jobs() -> list[str]:
	global job_scheduler

	ids: list[str] = []
	for job in job_scheduler.get_jobs():
		ids.append(job.id)

	return ids
