import os

from typing import Any
from logging import Logger, getLogger
from flask import Flask, current_app
from flask_redis import FlaskRedis
from clockpi.consts import *

redis_client = None
redis_thread = None
logger: Logger = getLogger(__name__)


def exception_handler(ex, pubsub, thread):
	logger.warning(f"exception_handler")
	thread.stop()
	thread.join(timeout=1.0)
	pubsub.close()


def unsub_from_channel() -> None:
	global redis_client
	redis_pubsub = redis_client.pubsub()
	redis_pubsub.unsubscribe(CHANNEL_CLOCKPI)

	"""
	redis_thread.stop()
	redis_thread.join(timeout=1.0)

	redis_pubsub = redis_client.pubsub()
	redis_pubsub.close()
	"""


def sub_to_channel() -> None:
	logger.info(f"Subscribing to {CHANNEL_CLOCKPI}")

	global redis_client
	redis_pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
	redis_pubsub.subscribe(**{f"{CHANNEL_CLOCKPI}": event_handler})

	# global redis_thread
	global redis_thread
	redis_thread = redis_pubsub.run_in_thread(
		sleep_time=0.1, exception_handler=exception_handler
	)
	redis_thread.name = "redis pubsub thread"


def init_app(app: Flask) -> None:
	logger.info(f"Initializing redis client")
	global redis_client
	redis_client = FlaskRedis(app, decode_responses=True)
	redis_client.set(SETTINGS_EPD_BUSY, "0")
	redis_client.set(SETTINGS_DRAW_GRIDS, "0")


def event_handler(msg) -> None:
	logger.info(msg=f"event_handler {msg=}")

	if (
		msg["type"] != "message"
		or msg["channel"] != CHANNEL_CLOCKPI
		or len(msg["data"]) == 0
	):
		return

	data: list[str] = msg["data"].split("^")
	if data[0] == MSG_BUSY:
		# get notification from epd-pi that epd_busy has been updated
		...

	elif data[0] == MSG_RESULT:
		# get notification from epd-pi that changes to the display has finished
		...


def rget(key: str, default: str) -> str:
	global redis_client
	value: Any = redis_client.get(key)
	if value is None:
		return default
	else:
		return value


def rset(key: str, value: str) -> None:
	global redis_client
	redis_client[key] = value


def rpublish(msg: str) -> None:
	logger.info(f"rpublish {msg=}")

	global redis_client
	redis_client.publish(CHANNEL_EPDPI, msg)
