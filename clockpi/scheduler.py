from flask_apscheduler import APScheduler
from flask import Flask
from logging import Logger, getLogger

from clockpi import logic, queue

logger: Logger = getLogger(__name__)
scheduler = APScheduler()


@scheduler.task("interval", id="test", seconds=5)
def job_test() -> None:
    print("job_test")


@scheduler.task("cron", id="update_clock", minute="*")
def job_update_clock() -> None:
    with scheduler.app.app_context():
        logic.epd_update()


@scheduler.task("cron", id="queue_shift_next", hour="*")
def job_queue_shift_next() -> None:
    with scheduler.app.app_context():
        queue.shift_next()


def init(app: Flask) -> None:
    scheduler.init_app(app)
    scheduler.start()
