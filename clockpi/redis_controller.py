import os

import queue
from typing import Any
from logging import Logger, getLogger
from flask import Flask, app
from flask_redis import FlaskRedis
from clockpi.consts import *
from clockpi import logic, queue

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
	redis_pubsub.subscribe(**{f"{R_CHANNEL_CLOCKPI}": event_handler})

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
	redis_client.set(R_SETTINGS_DRAW_GRIDS, "0")


def event_handler(msg: dict) -> None:
	logger.info(msg=f"event_handler {msg=}")

	with app.app_context():
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

			if get_epd_busy():
				logger.info(f"epdpi is busy, unable process event")
				return

			sleep_status: SleepStatus = get_sleep_status()

			if data[1] == R_MSG_BTN_ONOFF:
				# ON/OFF button has been pressed
				if (
					sleep_status == SleepStatus.AWAKE
					or sleep_status == SleepStatus.PENDING_AWAKE
				):
					rset(R_SLEEP_STATUS, str(object=SleepStatus.SLEEP.value))
					logic.epd_clear()
				elif (
					sleep_status == SleepStatus.SLEEP
					or sleep_status == SleepStatus.PENDING_SLEEP
				):
					rset(R_SLEEP_STATUS, str(SleepStatus.AWAKE.value))
					logic.epd_update()

			elif data[1] == R_MSG_BTN_NEXT:
				# NEXT button has been pressed
				queue.shift_next()
				logic.epd_update()
				rset(R_SLEEP_STATUS, str(SleepStatus.AWAKE.value))


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


def get_epd_busy() -> bool:
	return True if rget(R_SETTINGS_EPD_BUSY, "0") == "1" else False


def get_draw_grids() -> bool:
	return True if rget(R_SETTINGS_DRAW_GRIDS, "0") == "1" else False


def get_sleep_status() -> SleepStatus:
	return SleepStatus(int(rget(R_SLEEP_STATUS, str(SleepStatus.AWAKE.value))))
