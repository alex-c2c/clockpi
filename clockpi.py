import atexit
import logging
import os

from logging import Logger, getLogger
from flask import Flask

from app import auth, clockpi, db, job_scheduler, redis_controller, sleep, queue
from app.consts import *

logging.basicConfig(level=logging.DEBUG)
logger: Logger = getLogger(__name__)


def on_app_exit() -> None:
	logger.info(f"on_app_exit")

	redis_controller.unsub_from_channel()


# MAIN
app: Flask = Flask(__name__)
app.config.from_object(os.environ["APP_SETTING"])

# DB
db.init_app(app)

# Blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(clockpi.bp)
app.register_blueprint(sleep.bp)

# add url
app.add_url_rule("/", endpoint="index")

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
