import atexit
import os
import tempfile
import logging

from flask import Flask, current_app
from flask_apscheduler import APScheduler

from . import db, auth, clockpi
from clockpi.redis_controller import init_app as redis_init_app
from clockpi.logic import epd_update
from clockpi.queue import generate_random_queue

LOGGER = logging.getLogger(name="__init__")

scheduler = APScheduler()

"""
@scheduler.task("interval", id="test_job", seconds=5)
def test_job() -> None:
    print("test_job")
"""


@scheduler.task("cron", id="update_clock", minute="*")
def update_clock() -> None:
    with scheduler.app.app_context():
        epd_update()


@scheduler.task("cron", id="update_image", hour="*")
def update_image() -> None:
    with scheduler.app.app_context():
        pass


def on_app_exit() -> None:
    LOGGER.info(f"on_app_exit")
    from clockpi.redis_controller import redis_client, redis_thread

    redis_thread.stop()
    redis_thread.join(timeout=1.0)

    redis_pubsub = redis_client.pubsub()
    redis_pubsub.close()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        MAX_CONTENT_LENGTH=16 * 1000 * 1000,
        DATABASE=os.path.join(app.instance_path, "clockpi.sqlite"),
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
        ),
        SCHEDULER_API_ENABLED=True,
        DIR_APP_UPLOAD=os.path.join(os.path.dirname(app.instance_path), "upload"),
        DIR_TMP_UPLOAD=os.path.join(tempfile.gettempdir(), "upload"),
        DIR_TMP_PROCESSED=os.path.join(tempfile.gettempdir(), "processed"),
    )

    # Create Redis app
    redis_init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(clockpi.bp)

    app.add_url_rule("/", endpoint="index")

    # Register exit callback
    atexit.register(on_app_exit)

    # Scheduler
    global scheduler
    scheduler.init_app(app)
    scheduler.start()
    
    # Generate randomized image queue
    with app.app_context():
        generate_random_queue()

    return app
