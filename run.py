import atexit
import logging

from flask import Flask

from app import clock, create_app, wallpaper
from app import auth, sleep, redis_controller, job_scheduler, queue
from logging import Logger, getLogger


logging.basicConfig(level=logging.DEBUG)
logger: Logger = getLogger(__name__)


def on_app_exit() -> None:
	logger.info(f"on_app_exit")
	redis_controller.unsub_from_channel()


app: Flask = create_app()

# Blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(clock.bp)
app.register_blueprint(queue.bp)
app.register_blueprint(sleep.bp)
app.register_blueprint(wallpaper.bp)


# Add URL
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


if __name__ == "__main__":
	app.run()
