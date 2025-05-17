import atexit
import logging

from flask import Flask

from app import auth, epd, main, queue, sleep, wallpaper
from app import create_app, redis_controller, job_scheduler
from logging import Logger, getLogger


logging.basicConfig(level=logging.DEBUG)
logger: Logger = getLogger(__name__)


def on_app_exit() -> None:
	logger.info(f"on_app_exit")
	redis_controller.unsub_from_channel()


app: Flask = create_app()


# Blueprints
auth.register_blueprint(app)
main.register_blueprint(app)
epd.register_blueprint(app)
queue.register_blueprint(app)
sleep.register_blueprint(app)
wallpaper.register_blueprint(app)


# Add URL
app.add_url_rule("/", endpoint="index")


# Redis
redis_controller.init_app(app)
redis_controller.sub_to_channel()


# Scheduler for jobs
job_scheduler.init(app)


# Register exit callback
atexit.register(on_app_exit)


# Generate randomized image queue
with app.app_context():
	queue.logic.generate_initial_queue()


if __name__ == "__main__":
	app.run()
