import logging
import os
import tempfile

from . import db, auth, clockpi
from flask import Flask
from celery import Celery, Task
from flask_redis import FlaskRedis
from clockpi.logic import redis_event_handler


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def redis_init_app(app: Flask) -> FlaskRedis:
    rc = FlaskRedis(app, decode_responses=True)
    rc.set("mode", "22")
    rc.set("color", "2")
    rc.set("shadow", "1")
    rc.set("image_id", "0")
    rc.set("draw_grids", "0")
    rc.set("epd_busy", "0")
    
    rp = rc.pubsub()
    rp.psubscribe(**{'epd': redis_event_handler})
    rp.run_in_thread(sleep_time=0.5)

    app.extensions["redis"] = rc
    app.extensions["redis-sub"] = rp
    
    return rc


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        MAX_CONTENT_LENGTH=16 * 1000 * 1000,
        DATABASE=os.path.join(app.instance_path, 'clockpi.sqlite'),
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
        ),
        DIR_APP_UPLOAD = os.path.join(os.path.dirname(app.instance_path), "upload"),
        DIR_TMP_UPLOAD = os.path.join(tempfile.gettempdir(), "upload"),
        DIR_TMP_PROCESSED = os.path.join(tempfile.gettempdir(), "processed"),
    )

    # Create Redis app
    redis_init_app(app)
    
    # Create Celery app
    celery_init_app(app)
    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
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
    #app.register_blueprint(redis.bp)
    
    app.add_url_rule('/', endpoint='index')

    return app
