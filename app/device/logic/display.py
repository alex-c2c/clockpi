import base64
import os
import zlib

from datetime import datetime
from logging import Logger, getLogger

from app import db, redis_controller
from app.consts import *
from app.device.logic import can_access_device
from app.lib.errors import api_abort, ErrorCode
from app.wallpaper.models import WallpaperModel

from ..models import DeviceModel

logger: Logger = getLogger(__name__)


def update_display(device_id: int, is_save_img: bool = False) -> None:
	logger.info(f"{device_id=} {is_save_img=}")
	
	device: DeviceModel | None = db.session.get(DeviceModel, device_id)

	if device is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
		
	current_wallpaper_id: int = 0 if len(device.queue) == 0 else device.queue[0]
	wallpaper: WallpaperModel | None = db.session.get(WallpaperModel, current_wallpaper_id)
	if wallpaper is None:
		logger.error(f"Unable to find wallpaper resource ({current_wallpaper_id=})")
		return

	file_path: str = os.path.join(DIR_APP_UPLOAD, wallpaper.file_name)
	if not os.path.isfile(file_path):
		logger.error(f"Unable to find wallpaper file: {file_path}")
		return

	time: str = f"{datetime.now().hour:02d}:{datetime.now().minute:02d}"
	x: float | None = wallpaper.label_x_per	# time label x position (anchor: top left)
	y: float | None = wallpaper.label_y_per	# time label y position (anchor: top left)
	w: float | None = wallpaper.label_w_per	# time label width (percentage of canvas width)
	h: float | None = wallpaper.label_h_per	# time label height (percentage of canvas height)
	width: int = device.width
	height: int = device.height
	color: str = wallpaper.color
	shadow: str = wallpaper.shadow
	draw_grids: bool = device.is_draw_grid
	
	if x is None or y is None or w is None or h is None:
		logger.error(f"Missing required argument")
		return
	
	data: str = ""
	if device.type == "epd7in3e":
		from app.epd7in3e.logic import process_image, convert_image_to_buffer
		
		image = process_image(file_path, time, x, y, w, h, width, height, color, shadow, draw_grids)
		buffer: list[int] = convert_image_to_buffer(image)
		compressed_bytes: bytes = zlib.compress(bytes(buffer))
		data = base64.b64encode(compressed_bytes).decode("utf-8")
		
		logger.debug(f"{len(image.tobytes())=}")
		logger.debug(f"{len(buffer)=}")
		logger.debug(f"{len(compressed_bytes)=}")
		logger.debug(f"{len(data)=}")
		#logger.debug((compressed_bytes))
		
		if is_save_img:
			test_img_file_path: str = os.path.join(DIR_TEST_IMG, f"{wallpaper.file_name}")
			logger.info(f"Saving test image: {test_img_file_path}")
			image.save(test_img_file_path)
	
	if len(data) == 0:
		logger.error(f"Empty byte array")
		return

	redis_controller.rpublish(f"{R_CH_DRAW}_{device.ipv4}", data)


def clear_display(device_id: int) -> None:
	logger.info(f"[clear_display] {device_id=}")
	
	device: DeviceModel | None = db.session.get(DeviceModel, device_id)
	
	if device is None:
		api_abort(ErrorCode.DEVICE_NOT_FOUND)
		
	redis_controller.rpublish(f"{R_CH_CLEAR}_{device.ipv4}", "clear")
