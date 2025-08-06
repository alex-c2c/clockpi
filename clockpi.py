import atexit
import logging

from flask import Flask
from flask_cors import CORS

from app import api, api_bp, auth, epd, main, queue, sleep, wallpaper
from app import create_app, redis_controller
from logging import Logger, getLogger


logging.basicConfig(level=logging.DEBUG)
logger: Logger = getLogger(__name__)


def on_app_exit() -> None:
	logger.info(f"on_app_exit")
	redis_controller.unsub_from_channel()


app: Flask = create_app()


# Blueprints
app.register_blueprint(api_bp)
auth.append_namespace(api)
epd.append_namespace(api)
main.append_namespace(api)
queue.append_namespace(api)
sleep.append_namespace(api)
wallpaper.append_namespace(api)
#api.add_namespace(auth.ns)
#api.add_namespace(epd.ns)
#api.add_namespace(main.ns)
#api.add_namespace(queue.ns)
#api.add_namespace(sleep.ns)
#api.add_namespace(wallpaper.ns)

# Add URL
#app.add_url_rule("/", endpoint="index")


# Redis
redis_controller.init_app(app)
redis_controller.sub_to_channel()


# Flask CORS x Nextjs
CORS(app, supports_credentials=True, origins=['http://localhost:3000'])


# Register exit callback
atexit.register(on_app_exit)


# Generate randomized image queue
with app.app_context():
	from app.queue.logic import generate_initial_queue
	generate_initial_queue()
 
logger.info("URLS")
logger.info(app.url_map)


'''
if __name__ == "__main__":
	logger.warning("TEST TEST")
	app.run()
'''
