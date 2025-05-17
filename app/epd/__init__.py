from logging import Logger, getLogger
from flask import Flask


logger: Logger = getLogger(__name__)


def register_blueprint(app: Flask) -> None:
	from .routes import bp
	app.register_blueprint(bp)
