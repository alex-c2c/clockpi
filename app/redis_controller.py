import queue
from typing import Any
from logging import Logger, getLogger
from flask import Flask
from flask_redis import FlaskRedis

from app.consts import *
from app import epd, queue, sleep


logger: Logger = getLogger(__name__)


def exception_handler(ex, pubsub, thread):
	logger.warning(f"exception_handler")
	thread.stop()
	thread.join(timeout=1.0)
	pubsub.close()


def unsub_from_channel() -> None:
	global redis_client
	redis_pubsub = redis_client.pubsub()
	redis_pubsub.unsubscribe(R_CHANNEL_CLOCKPI)

	"""
	redis_thread.stop()
	redis_thread.join(timeout=1.0)

	redis_pubsub = redis_client.pubsub()
	redis_pubsub.close()
	"""


def sub_to_channel() -> None:
	logger.info(f"Subscribing to {R_CHANNEL_CLOCKPI}")

	global redis_client
	redis_pubsub = redis_client.pubsub(ignore_subscribe_messages=True)

	"""
	Note:
 	Running Flask in development mode means "auto-reload" is turned on, thus this will cause
	the application to spawn 2 instances, 1 for code execution, 1 for comparison to do hot-reload,
	which in turn causes 2 redis-subscriber to be spawn, leading to 2 event_handler method to be called whenever there is a message.
	To bypass this during development, run flask with --no-reload option.
 	"""
	redis_pubsub.subscribe(**{f"{R_CHANNEL_CLOCKPI}": event_handler})

	"""
	Running redis subscribe in a seperate thread because otherwise, need to implement it
	in a while loop which will block the main code from running.
 	"""
	global redis_thread
	redis_thread = redis_pubsub.run_in_thread(
		sleep_time=0.1, exception_handler=exception_handler
	)
	redis_thread.name = "redis pubsub thread"


def init_app(app: Flask) -> None:
	logger.info(f"Initializing redis client")
	global redis_client
	redis_client = FlaskRedis(app, decode_responses=True)
	redis_client.set(R_SETTINGS_DRAW_GRIDS, "0")


def event_handler(msg: dict) -> None:
	logger.info(msg=f"event_handler {msg=}")

	if (
		msg["type"] != "message"
		or msg["channel"] != R_CHANNEL_CLOCKPI
		or len(msg["data"]) == 0
	):
		return

	data: list[str] = msg["data"].split("^")
	if data[0] == R_MSG_BUSY:
		# get notification from epd-pi that epd_busy has been updated
		...

	elif data[0] == R_MSG_RESULT:
		# get notification from epd-pi that changes to the display has finished
		...

	elif data[0] == R_MSG_BTN:
		# get notification from epd-pi that a button has been pressed

		if epd.logic.get_busy():
			logger.info(f"epdpi is busy, unable process event")
			return

		sleep_status: int = sleep.logic.get_status()

		if data[1] == R_MSG_BTN_ONOFF:
			# ON/OFF button has been pressed
			if (sleep_status == SLEEP_STATUS_AWAKE):
				rset(R_SLEEP_STATUS, str(object=SLEEP_STATUS_SLEEP))
				epd.logic.clear()
			elif (sleep_status == SLEEP_STATUS_SLEEP):
				rset(R_SLEEP_STATUS, str(SLEEP_STATUS_AWAKE))
				epd.logic.update()

		elif data[1] == R_MSG_BTN_NEXT:
			# NEXT button has been pressed
			queue.logic.shift_next()
			epd.logic.update()
			rset(R_SLEEP_STATUS, str(SLEEP_STATUS_AWAKE))


def rdelete(key: str) -> None:
	global redis_client
	redis_client.delete(key)


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
	redis_client.publish(R_CHANNEL_EPDPI, msg)


def get_draw_grids() -> bool:
	return True if rget(R_SETTINGS_DRAW_GRIDS, "0") == "1" else False
