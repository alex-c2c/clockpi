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


# @job_scheduler.task("cron", id="update_clock", minute="*")
def job_update_clock() -> None:
    with job_scheduler.app.app_context():
        logic.epd_update()


# @job_scheduler.task("cron", id="queue_shift_next", hour="*")
def job_queue_shift_next() -> None:
    with job_scheduler.app.app_context():
        queue.shift_next()


def init(app: Flask) -> None:
    job_scheduler.init_app(app)
    job_scheduler.start()


def validate_cron_time(hr: int, min: int, days: tuple[int, ...]) -> bool:
    if hr < 0 or hr > 23:
        logger.error(f"Invalid hour")
        return False

    if min < 0 or min > 59:
        logger.error(f"Invalid minute")
        return False

    if len(days) == 0 or len(days) > 7:
        logger.error(f"Invalid number of days")
        return False

    for day in days:
        if day < 0 or day > 6:
            logger.error(f"invalid day")
            return False

    return True


def add_or_update_cron_job(
    id: str, func: Callable, hr: int, min: int, days: tuple[int, ...]
) -> bool:
    logger.info(f"add_or_update_cron_job, {id=} {hr=} {min=} {days=}")

    # Validate cron timing
    validation_result: bool = validate_cron_time(hr, min, days)
    if not validation_result:
        return False

    # Convert tuple[bool] to day_of_week string
    day_of_week: str = ""
    for d in range(len(days)):
        if days[d]:
            day_of_week += f"{str(d)},"

    if len(day_of_week) > 1:
        day_of_week = day_of_week[:-1]
    # day_of_week: str = ",".join(str(d) for d in days)
    logger.debug(day_of_week)

    # Try to
    global job_scheduler
    job_scheduler.add_job(
        id,
        func,
        trigger="cron",
        replace_existing=True,
        hour=hr,
        minute=min,
        day_of_week=day_of_week,
    )


def remove_cron_job(id: str) -> bool:
    try:
        job_scheduler.remove_job(id)
        return True
    except JobLookupError as error:
        logger.error(f"Attempting to remove invalid job id: {id}, {error=}")
        return False
