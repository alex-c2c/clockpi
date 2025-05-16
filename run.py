import atexit
import logging

from flask import Flask

from app import create_app
from app import redis_controller, job_scheduler
from logging import Logger, getLogger

from app.auth.routes import bp as auth_bp
from app.epd.routes import bp as epd_bp
from app.main.routes import bp as main_bp
from app.queue.routes import bp as queue_bp
from app.sleep.routes import bp as sleep_bp
from app.wallpaper.routes import bp as wallpaper_bp
from app import queue


logging.basicConfig(level=logging.DEBUG)
logger: Logger = getLogger(__name__)


def on_app_exit() -> None:
	logger.info(f"on_app_exit")
	redis_controller.unsub_from_channel()


app: Flask = create_app()


# Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(epd_bp)
app.register_blueprint(queue_bp)
app.register_blueprint(sleep_bp)
app.register_blueprint(wallpaper_bp)


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
