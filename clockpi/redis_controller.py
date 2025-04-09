import os
import logging

from typing import Any
from flask import Flask, current_app
from flask_redis import FlaskRedis
from clockpi.consts import *

redis_client = None
redis_thread = None

LOGGER = logging.getLogger(name="redis_controller")


def init_app(app: Flask):
    global redis_client
    redis_client = FlaskRedis(app, decode_responses=True)
    redis_client.set(SETTINGS_EPD_BUSY, "0")
    redis_client.set(SETTINGS_IMAGE_ID, "0")
    redis_client.set(SETTINGS_MODE, "22")
    redis_client.set(SETTINGS_COLOR, "2")
    redis_client.set(SETTINGS_SHADOW, "1")
    redis_client.set(SETTINGS_DRAW_GRIDS, "0")

    redis_pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
    redis_pubsub.subscribe(**{f"{CHANNEL_CLOCKPI}": event_handler})

    # global redis_thread
    global redis_thread
    redis_thread = redis_pubsub.run_in_thread(
        sleep_time=0.1, exception_handler=exception_handler
    )
    redis_thread.name = "redis pubsub thread"


def event_handler(msg) -> None:
    LOGGER.info(msg=f"event_handler {msg=}")

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


def exception_handler(ex, pubsub, thread):
    LOGGER.warning(f"exception_handler")
    thread.stop()
    thread.join(timeout=1.0)
    pubsub.close()


def rget(key: str, default: str) -> str:
    global redis_client
    redis_client = current_app.extensions["redis"]
    value: Any = redis_client.get(key)
    if value is None:
        return default
    else:
        return value


def rset(key: str, value: str) -> None:
    global redis_client
    redis_client = current_app.extensions["redis"]
    redis_client[key] = value


def get_settings() -> tuple[int, int, int, int, bool]:
    image_id: int = int(rget(SETTINGS_IMAGE_ID, "0"))
    mode: int = int(rget(SETTINGS_MODE, "22"))
    color: int = int(rget(SETTINGS_COLOR, "2"))
    shadow: int = int(rget(SETTINGS_SHADOW, "1"))
    draw_grids: bool = True if rget(SETTINGS_DRAW_GRIDS, "0") == "1" else False

    return image_id, mode, color, shadow, draw_grids


def reset_settings() -> None:
    LOGGER.debug(f"rset_defaults")

    rset(SETTINGS_IMAGE_ID, "0")
    rset(SETTINGS_MODE, "22")
    rset(SETTINGS_COLOR, "2")
    rset(SETTINGS_SHADOW, "1")
    rset(SETTINGS_DRAW_GRIDS, "0")


def rpublish(msg: str) -> None:
    global redis_client
    redis_client.publish(CHANNEL_EPDPI, msg)
