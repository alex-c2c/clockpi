import atexit

from flask import Flask
from flask_cors import CORS

from app import api, api_bp, auth, epd, main, queue, session_pkg, schedule, user, wallpaper
from app import create_app, redis_controller
from logging import Logger, getLogger


logger: Logger = getLogger(__name__)
logger.info("running clockpi.py")


def on_app_exit() -> None:
	logger.info(f"on_app_exit")
	redis_controller.unsub_from_channel()


app: Flask = create_app()


# API Blueprint + namespaces
app.register_blueprint(api_bp)
auth.append_namespace(api)
epd.append_namespace(api)
main.append_namespace(api)
queue.append_namespace(api)
session_pkg.append_namespace(api)
schedule.append_namespace(api)
user.append_namespace(api)
wallpaper.append_namespace(api)


# Redis
redis_controller.init_app(app)
#redis_controller.sub_to_channel()


# Flask CORS x Nextjs
CORS(app, supports_credentials=True, origins=['http://localhost:3000'])


# Register exit callback
atexit.register(on_app_exit)
