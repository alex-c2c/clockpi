import hashlib
import os
import shutil

from datetime import datetime
from logging import Logger, getLogger

from pytz import timezone
from sqlalchemy import delete, select
from flask import request
from flask.ctx import AppContext
from werkzeug.datastructures import FileStorage, ImmutableMultiDict
from werkzeug.utils import secure_filename

from app import db
from app.consts import *
from app.device.logic import can_access_device
from app.device.models import DeviceModel
from app.epd7in3e.consts import *
from app.device.logic.queue import append_to_queue, remove_from_queue
from app.lib.errors import api_abort, ErrorCode

from .consts import ALLOWED_EXTENSIONS
from .models import WallpaperModel
from .utils import save_upload_file, validate_image, process_image


logger: Logger = getLogger(__name__)


"""""
LOGIC
"""""


def create_wallpaper(
	user_id:int,
	device_id: int,
	file: FileStorage | None,
	form_data: ImmutableMultiDict
) -> None:
	logger.info(f"Attempting to create wallpaper: {user_id=} {device_id=} {file=} {form_data=}")
	
	img_scale_per_str: str | None = form_data.get("imgScalePer")
	x_pos_per_str: str | None = form_data.get("xPosPer")
	y_pos_per_str: str | None = form_data.get("yPosPer")

	secured_file_name: str = save_upload_file(file)
	
	failed_validations: dict = {}
	
	if img_scale_per_str is None:
		failed_validations["imgScalePer"] = "This is a required field."
	else:
		try:
			img_scale_per: float = float(img_scale_per_str)
		except ValueError as e:
			failed_validations["imgScalePer"] =  "Invalid input (float required)."
	
	if x_pos_per_str is None:
		failed_validations["xPosPer"] = "This is a required field."
	else:
		try:
			x_pos_per: float = float(x_pos_per_str)
		except ValueError as e:
			failed_validations["xPosPer"] =  "Invalid input (float required)."
			
	if y_pos_per_str is None:
		failed_validations["yPosPer"] = "This is a required field."
	else:
		try:
			y_pos_per: float = float(y_pos_per_str)
		except ValueError as e:
			failed_validations["yPosPer"] =  "Invalid input (float required)."
	
	if len(failed_validations.values()) > 0:
		api_abort(ErrorCode.VALIDATION_ERROR, errors=failed_validations)
	
	device: DeviceModel | None = db.session.get(DeviceModel, device_id)
	if device is None:
		api_abort(ErrorCode.INVALID_DEPENDENCY, detail="Device not found")

	temp_upload_path: str = os.path.join(DIR_TMP_UPLOAD, secured_file_name)

	# Remove temp file and abort if there are input errors	
	if not can_access_device(user_id, device_id):
		os.remove(temp_upload_path)
		api_abort(ErrorCode.INVALID_DEPENDENCY, detail="Unable to access device")

	# validate image
	if not validate_image(temp_upload_path):
		os.remove(path=temp_upload_path)
		logger.error(f"Invalid image file")
		api_abort(ErrorCode.UNPROCESSABLE_ENTITY)

	# process image
	if not os.path.isdir(DIR_TMP_PROCESSED):
		os.mkdir(DIR_TMP_PROCESSED)

	temp_processed_path: str = os.path.join(DIR_TMP_PROCESSED, secured_file_name)
	process_result: bool = process_image(
		file_path=temp_upload_path,
		dest_path=temp_processed_path,
		canvas_size=(device.width, device.height),
		image_scale=img_scale_per,
		image_offset=(int(device.width * x_pos_per), int(device.height * y_pos_per)),
		nc=EPD_NC,
	)

	if not process_result:
		if os.path.isfile(temp_upload_path):
			os.remove(temp_upload_path)
		if os.path.isfile(temp_processed_path):
			os.remove(temp_processed_path)
		logger.error(f"Unable to proccess image")
		api_abort(ErrorCode.INTERNAL_SERVER_ERROR)

	# get hash of processed image
	try:
		h = hashlib.sha256()
		with open(temp_processed_path, "rb") as f:
			while True:
				chunk = f.read(h.block_size)
				if not chunk:
					break
				h.update(chunk)
		hash: str = h.hexdigest()

	except OSError as error:
		if os.path.isfile(temp_upload_path):
			os.remove(temp_upload_path)
		if os.path.isfile(temp_processed_path):
			os.remove(temp_processed_path)
		logger.error(f"Unable to obtain file hash: {error}")
		api_abort(ErrorCode.INTERNAL_SERVER_ERROR)

	# copy processed image to upload dir
	try:
		new_file_name: str = f"{hash[0:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bmp"
		dest_path: str = os.path.join(DIR_APP_UPLOAD, new_file_name)
		logger.debug(f"{dest_path=}")
		shutil.copy2(temp_processed_path, dest_path)
		os.remove(temp_processed_path)

	except OSError as error:
		if os.path.isfile(temp_upload_path):
			os.remove(temp_upload_path)
		if os.path.isfile(temp_processed_path):
			os.remove(temp_processed_path)
		logger.error(f"Unable to copy file due to {error}")
		api_abort(ErrorCode.INTERNAL_SERVER_ERROR)
		return

	# Save upload entry to DB
	try:
		name: str = secured_file_name.rsplit(".", 1)[0]
		file_size: int = os.path.getsize(dest_path)

		# Insert to DB
		wm: WallpaperModel = WallpaperModel()
		wm.device_id = device_id
		wm.name = name
		wm.hash = hash
		wm.file_name = new_file_name
		wm.size = file_size
		wm.color = device.default_label_color
		wm.shadow = device.default_label_shadow
		
		db.session.add(wm)
		db.session.flush()

		# Append to image queue
		append_to_queue(user_id, device_id, wm.id)

	except OSError as error:
		logger.error(f"Unable to create new wallpaper model due to {error}")
		api_abort(ErrorCode.DATABASE_ERROR)

	logger.info(f"Processed image and created new wallpaper model")


def delete_wallpaper(user_id: int, wallpaper_id: int) -> None:
	logger.info(msg=f"Attempting to delete wallpaper {wallpaper_id=}")

	wallpaper: WallpaperModel | None = db.session.get(WallpaperModel, wallpaper_id)
	if wallpaper is None:
		api_abort(ErrorCode.WALLPAPER_NOT_FOUND)
	
	device_id: int = wallpaper.device_id
	if not can_access_device(user_id, device_id):
		api_abort(ErrorCode.FORBIDDEN)

	file_name: str = wallpaper.file_name
	file_path: str = os.path.join(DIR_APP_UPLOAD, file_name)

	try:
		db.session.delete(wallpaper)
		db.session.commit()
	except Exception as e:
		logger.error(f"Unable to delete wallpaper model due to {e}")
		api_abort(ErrorCode.INTERNAL_SERVER_ERROR)

	remove_from_queue(user_id, device_id, wallpaper_id)

	if os.path.isfile(file_path):
		try:
			os.remove(file_path)
		except Exception as ex:
			logger.error(f"Unable to delete wallpaper file due to {ex}")
	else:
		logger.error(f"Unable to find wallpaper file {file_path}")

	logger.info(f"Deleted wallpaper {wallpaper_id=}")
	

def update_wallpaper(user_id: int, wallpaper_id: int, payload: dict) -> None:
	logger.info(f"Attempting to update wallpaper {wallpaper_id=}")

	wallpaper: WallpaperModel | None = db.session.get(WallpaperModel, wallpaper_id)
	if wallpaper is None:
		api_abort(ErrorCode.WALLPAPER_NOT_FOUND)
		
	if not can_access_device(user_id, wallpaper.device_id):
		api_abort(ErrorCode.FORBIDDEN, details="Unable to access device")
		
	device: DeviceModel | None = db.session.get(DeviceModel, wallpaper.device_id)
	if device is None:
		api_abort(ErrorCode.INVALID_DEPENDENCY, detail="Device not found")
	
	if not can_access_device(user_id, wallpaper.device_id):
		api_abort(ErrorCode.FORBIDDEN, detail="Unable to access device")

	failed_validations: dict = {}
	
	x: int | None = payload.get("x")
	if x is not None:
		if x < 0 or x > 100:
			failed_validations["x"] = "Invalid input (0 >= x <= 100)"
		wallpaper.label_x_per = x

	y: int | None = payload.get("y")
	if y is not None:
		if y < 0 or y > 100:
			failed_validations["y"] = "Invalid input (0 >= y <= 100)"
		wallpaper.label_y_per = y

	w: int | None = payload.get("w")
	if w is not None:
		if w <= 0 or w > 100:
			failed_validations["w"] = "Invalid input (0 > w <= 100)"
		wallpaper.label_w_per = w

	h: int | None = payload.get("h")
	if h is not None:
		if h <= 0 or h > 100:
			failed_validations["h"] = "Invalid input (0 > h <= 100)"
		wallpaper.label_h_per = h

	color: str | None = payload.get("color")
	if color is not None:
		if color.upper() not in device.supported_colors:
			failed_validations["color"] = "Invalid input (Unsupported color)"
		wallpaper.color = color.upper()

	shadow: int | None = payload.get("shadow")
	if shadow is not None:
		if shadow.upper() not in device.supported_colors:
			failed_validations["shadow"] = "Invalid input (Unsupported color)"
		wallpaper.shadow = shadow.upper()

	if len(failed_validations.values()) > 0:
		api_abort(ErrorCode.VALIDATION_ERROR, errors=failed_validations)

	wallpaper.updated_at = datetime.now(timezone("Asia/Singapore"))

	try:
		db.session.commit()
	except Exception as e:
		logger.error(f"Unable to update wallpaper due to {e}")
		api_abort(ErrorCode.DATABASE_ERROR)

	logger.info(f"Wallpaper {wallpaper_id=} updated")


def get_wallpaper_name(user_id: int, wallpaper_id: int | None) -> str:
	model: WallpaperModel | None = db.session.get(WallpaperModel, wallpaper_id)
	if model is None:
		api_abort(ErrorCode.WALLPAPER_NOT_FOUND)
	
	if not can_access_device(user_id, model.device_id):
		api_abort(ErrorCode.FORBIDDEN, detail="Unable to access device")
		
	file_name: str = model.file_name
	file_path: str = os.path.join(DIR_APP_UPLOAD, f"{file_name}")
	if not os.path.isfile(file_path):
		api_abort(ErrorCode.WALLPAPER_NOT_FOUND, detail="Wallpaper image file not found")

	return file_name


def get_wallpapers(user_id: int, device_id:int) -> list[dict]:
	if not can_access_device(user_id, device_id):
		api_abort(ErrorCode.FORBIDDEN, detail="Unable to access device")
	
	stmt = select(WallpaperModel).where(WallpaperModel.device_id == device_id)
	models: list[WallpaperModel] = list(db.session.scalars(stmt).all())
	
	wallpapers: list[dict] = []
	for model in models:
		wallpapers.append(model.to_dict())

	return wallpapers
