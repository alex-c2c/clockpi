import atexit
import logging

from logging import Logger, getLogger
from flask import Flask

from clockpi import create_app, job_scheduler, redis_controller, sleep, queue
from clockpi.consts import *

logging.basicConfig(level=logging.DEBUG)
logger: Logger = getLogger(__name__)


def on_app_exit() -> None:
	logger.info(f"on_app_exit")

	redis_controller.unsub_from_channel()


# MAIN
app: Flask = create_app()

# Redis
redis_controller.init_app(app)
redis_controller.sub_to_channel()

# Sleep Schedule
sleep.init(app)

# Scheduler for jobs
job_scheduler.init(app)

# Register exit callback
atexit.register(on_app_exit)

# Generate randomized image queue
with app.app_context():
	queue.generate_initial_queue()
