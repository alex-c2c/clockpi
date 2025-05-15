import os
from typing import Callable
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

