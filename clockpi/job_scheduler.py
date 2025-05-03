from csv import Error
from typing import Callable
from flask_apscheduler import APScheduler
from apscheduler.jobstores.base import JobLookupError, ConflictingIdError
from flask import Flask
from logging import Logger, getLogger

from clockpi import logic, queue

logger: Logger = getLogger(__name__)
job_scheduler = APScheduler()


# @job_scheduler.task("interval", id="test", seconds=5)
def job_test() -> None:
	print("job_test")


@job_scheduler.task("cron", id="update_clock", minute="*")
def job_update_clock() -> None:
	with job_scheduler.app.app_context():
		logic.epd_update()


@job_scheduler.task("cron", id="queue_shift_next", hour="*")
def job_queue_shift_next() -> None:
	with job_scheduler.app.app_context():
		queue.shift_next()


def init(app: Flask) -> None:
	job_scheduler.init_app(app)
	job_scheduler.start()


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
		day_of_week=f"{day}",
	)


def remove_cron_job(id: str) -> bool:
	try:
		job_scheduler.remove_job(id)
		return True
	except JobLookupError as error:
		logger.error(f"Attempting to remove invalid job id: {id}, {error=}")
		return False


def get_cron_jobs():
	return job_scheduler.get_jobs(jobstore="sleep")
