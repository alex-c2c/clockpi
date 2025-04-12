import atexit
from logging import Logger, getLogger
from flask import Flask
from flask_apscheduler import APScheduler

from clockpi import create_app
from clockpi import redis_controller
from clockpi.consts import *
from clockpi.logic import epd_update
from clockpi.queue import generate_random_queue

logger: Logger = getLogger(__name__)
logger.info(f"app.py")
scheduler = APScheduler()


@scheduler.task("interval", id="test", seconds=5)
def job_test() -> None: ...


@scheduler.task("cron", id="update_clock", minute="*")
def job_update_clock() -> None:
    with scheduler.app.app_context():
        epd_update()


@scheduler.task("cron", id="update_image", hour="*")
def job_update_image() -> None:
    with scheduler.app.app_context():
        pass


def on_app_exit() -> None:
    logger.info(f"on_app_exit")

    redis_controller.unsub_from_channel()


if __name__ == "__main__":
    # MAIN
    app: Flask = create_app()

    # Redis
    redis_controller.init_app(app)
    redis_controller.sub_to_channel()

    # Scheduler for jobs
    scheduler.init_app(app)
    scheduler.start()

    # Register exit callback
    atexit.register(on_app_exit)

    # Generate randomized image queue
    with app.app_context():
        generate_random_queue()
