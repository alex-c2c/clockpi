import os
import tempfile

from logging import Logger, getLogger
from flask import Flask

from . import db, auth, clockpi, sleep


logger: Logger = getLogger(__name__)


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth.bp)
    app.register_blueprint(clockpi.bp)
    app.register_blueprint(sleep.bp)


def add_url(app: Flask) -> None:
    app.add_url_rule("/", endpoint="index")


def create_app(test_config=None):
    logger.info(f"create_app")

    # create and configure the app
    app: Flask = Flask(__name__, instance_relative_config=True)
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

    # initialize database
    db.init_app(app)

    # register blueprints
    register_blueprints(app)

    # add url
    add_url(app)

    return app
