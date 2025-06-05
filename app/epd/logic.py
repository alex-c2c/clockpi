import os

from datetime import datetime
from flask import current_app
from logging import Logger, getLogger

from app.consts import *
from app.models import WallpaperModel
from app import redis_controller
from app.queue import logic


logger: Logger = getLogger(__name__)


def get_busy() -> bool:
	return True if redis_controller.rget(R_SETTINGS_EPD_BUSY, "0") == "1" else False


def update_display() -> None:
	logger.debug(f"update_display")

	draw_grids: bool = redis_controller.get_draw_grids()
	image_queue: tuple[int] = logic.get_queue()

	if len(image_queue) == 0:
		return

	wallpaper = WallpaperModel.query.get(image_queue[0])
	hash: str = wallpaper.hash if wallpaper is not None else ""

	if len(hash) > 0:
		file_path: str = os.path.join(
			current_app.config["DIR_APP_UPLOAD"], f"{hash}.bmp"
		)
		if not os.path.isfile(file_path):
			file_path = ""

	time: str = f"{datetime.now().hour:02d}:{datetime.now().minute:02d}"
	mode: str = wallpaper.mode
	color: str = wallpaper.color
	shadow: str = wallpaper.shadow

	redis_controller.rpublish(
		f"{R_MSG_DRAW}^{file_path}^{time}^{mode}^{color}^{shadow}^{'1' if draw_grids else '0'}"
	)


def update_display_with_buffer():
     ...


def clear_display() -> None:
	logger.debug(f"clear")
	redis_controller.rpublish(R_MSG_CLEAR)
