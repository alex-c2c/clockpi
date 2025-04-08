import logging

from threading import Thread
from typing import Any
from flask import Flask
from flask_redis import FlaskRedis
from clockpi.consts import *


redis_client: FlaskRedis | None = None
redis_pubsub: Any | None = None
redis_thread: Thread | None = None


def redis_init_app(app: Flask) -> FlaskRedis:
    global redis_client
    redis_client = FlaskRedis(app, decode_responses=True)
    redis_client.set(SETTINGS_EPD_BUSY, "0")
    redis_client.set(SETTINGS_IMAGE_ID, "0")
    redis_client.set(SETTINGS_MODE, "22")
    redis_client.set(SETTINGS_COLOR, "2")
    redis_client.set(SETTINGS_SHADOW, "1")
    redis_client.set(SETTINGS_DRAW_GRIDS, "0")

    global redis_pubsub
    redis_pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
    redis_pubsub.subscribe(**{f"{CHANNEL_CLOCKPI}": event_handler})

    # global redis_thread
    redis_thread = redis_pubsub.run_in_thread(
        sleep_time=0.1, exception_handler=exception_handler
    )
    redis_thread.name = "redis pubsub thread"

    return redis_client


def event_handler(msg) -> None:
    logging.debug(msg=f"event_handler {msg=}")

    if msg["type"] != "message" or msg["channel"] != CHANNEL_CLOCKPI or len(msg["data"]) == 0:
        return

    data: list[str] = msg["data"].split("^")
    if data[0] == MSG_BUSY:
        # get notification from epd-pi that epd_busy has been updated
        ...


def exception_handler(ex, pubsub, thread):
    thread.stop()
    thread.join(timeout=1.0)
    pubsub.close()


def publish_epdpi_draw(file_path: str, time: str) -> None:
    global redis_client

    _, mode, color, shadow, draw_grids = get_clockpi_settings()

    redis_client.publish(
        CHANNEL_EPDPI,
        f"{MSG_DRAW}^{file_path}^{time}^{mode}^{color}^{shadow}^{'1' if draw_grids else '0'}",
    )


def publish_epdpi_clear() -> None:
    global redis_client
    redis_client.publish(CHANNEL_EPDPI, MSG_CLEAR)


def redis_get(key: str, default: str) -> str:
    global redis_client
    value: Any = redis_client.get(key)
    if value is None:
        return default
    else:
        return value


def redis_set(key: str, value: str) -> None:
    global redis_client
    redis_client[key] = value


def get_clockpi_settings() -> tuple[int, int, int, int, bool]:
    global redis_client

    image_id: int = int(redis_get(SETTINGS_IMAGE_ID, "0"))
    mode: int = int(redis_get(SETTINGS_MODE, "22"))
    color: int = int(redis_get(SETTINGS_COLOR, "2"))
    shadow: int = int(redis_get(SETTINGS_SHADOW, "1"))
    draw_grids: bool = True if redis_get(SETTINGS_DRAW_GRIDS, "0") == "1" else False

    return image_id, mode, color, shadow, draw_grids


def get_clockpi_image_id() -> int:
    return int(redis_get(SETTINGS_IMAGE_ID, "0"))


def set_clockpi_defaults() -> None:
    logging.debug(f"set_clockpi_defaults")

    redis_set(SETTINGS_IMAGE_ID, "0")
    redis_set(SETTINGS_MODE, "22")
    redis_set(SETTINGS_COLOR, "2")
    redis_set(SETTINGS_SHADOW, "1")
    redis_set(SETTINGS_DRAW_GRIDS, "0")


def set_clockpi_image_id(id: int) -> None:
    redis_set(SETTINGS_IMAGE_ID, str(id))


def set_clockpi_mode(mode: int) -> None:
    redis_set(SETTINGS_MODE, str(mode))


def set_clockpi_color(color: int) -> None:
    redis_set(SETTINGS_COLOR, str(color))


def set_clockpi_shadow(shadow: int) -> None:
    redis_set(SETTINGS_SHADOW, str(shadow))


def set_clockpi_draw_grids(draw_grids: bool) -> None:
    redis_set(SETTINGS_DRAW_GRIDS, "1" if draw_grids else "0")


def get_epd_busy() -> bool:
    busy: bool = True if redis_get(SETTINGS_EPD_BUSY, "0") == "1" else False
    return busy
