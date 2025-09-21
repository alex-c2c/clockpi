import hashlib
import os
import shutil

from datetime import datetime
from logging import Logger, getLogger
from typing import Sequence

from pytz import timezone
from sqlalchemy import and_, delete, select
from werkzeug.datastructures import FileStorage, ImmutableMultiDict

from app import db
from app.consts import *
from app.device.logic import can_access_device
from app.device.models import DeviceModel
from app.epd7in3e.consts import *
from app.device.logic.queue import append_to_queue, remove_from_queue
from app.lib.errors import api_abort, ErrorCode

from .models import WallpaperModel, WallpaperOwnershipModel
from .utils import save_upload_file, validate_image, process_image


logger: Logger = getLogger(__name__)


"""""
LOGIC
"""""


def can_access_wallpaper(user_id: int, device_id: int, wallpaper_id: int | None) -> bool:
	stmt = select(WallpaperOwnershipModel).where(
		and_(
			WallpaperOwnershipModel.user_id == user_id,
			WallpaperOwnershipModel.device_id == device_id,
			WallpaperOwnershipModel.wallpaper_id == wallpaper_id
			))
	if db.session.scalars(stmt).one_or_none() is None:
		return False
		
	return True


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
	name: str = secured_file_name.rsplit(".", 1)[0]
	file_size: int = os.path.getsize(dest_path)

	# create new WallpaperModel
	wm: WallpaperModel = WallpaperModel()
	wm.name = name
	wm.hash = hash
	wm.file_name = new_file_name
	wm.size = file_size
	wm.color = device.default_label_color
	wm.shadow = device.default_label_shadow
	
	db.session.add(wm)
	db.session.flush()
	
	# create new WallpaperOwnershipModel
	wom: WallpaperOwnershipModel = WallpaperOwnershipModel()
	wom.wallpaper_id = wm.id
	wom.user_id = user_id
	wom.device_id = device_id
	
	db.session.add(wom)
	db.session.flush()

	# this method will execute the commit()
	append_to_queue(device_id, wm.id)

	logger.info(f"Processed image and created new wallpaper model")


def delete_wallpaper(device_id:int, wallpaper_id: int) -> None:
	logger.info(msg=f"Attempting to delete wallpaper {wallpaper_id=}")
	
	file_name: str = db.session.scalars(select(WallpaperModel.file_name).where(WallpaperModel.id == wallpaper_id)).one_or_none() or ""
	file_path: str = os.path.join(DIR_APP_UPLOAD, file_name)

	# delete wallpaper owership first (ForeignKey)
	db.session.execute(delete(WallpaperOwnershipModel).where(WallpaperOwnershipModel.wallpaper_id == wallpaper_id))
	db.session.flush()
	
	# delete wallpaper
	db.session.execute(delete(WallpaperModel).where(WallpaperModel.id == wallpaper_id))
	db.session.flush()
	
	# this method will execute the commit()
	remove_from_queue(device_id, wallpaper_id)

	if os.path.isfile(file_path):
		try:
			os.remove(file_path)
		except Exception as ex:
			logger.error(f"Unable to delete wallpaper file due to {ex}")
	else:
		logger.error(f"Unable to find wallpaper file {file_name} in {file_path}")

	logger.info(f"Deleted wallpaper {wallpaper_id=}")
	

def update_wallpaper(device_id: int, wallpaper_id: int, payload: dict) -> None:
	logger.info(f"Attempting to update wallpaper {wallpaper_id=}")

	wallpaper: WallpaperModel | None = db.session.get(WallpaperModel, wallpaper_id)
	if wallpaper is None:
		api_abort(ErrorCode.WALLPAPER_NOT_FOUND)
	
	supported_colors: list[str] = db.session.scalars(select(DeviceModel.supported_colors).where(DeviceModel.id == device_id)).one_or_none() or []
	
	failed_validations: dict = {}
	
	label_x_per: float| None = payload.get("labelXPer")
	if label_x_per is not None:
		if label_x_per < 0:
			failed_validations["labelXPer"] = "Invalid input (labelXPer >= 0)"
		wallpaper.label_x_per = label_x_per

	label_y_per: float | None = payload.get("labelYPer")
	if label_y_per is not None:
		if label_y_per < 0:
			failed_validations["labelYPer"] = "Invalid input (labelYPer >= 0)"
		wallpaper.label_y_per = label_y_per

	label_w_per: float | None = payload.get("labelWPer")
	if label_w_per is not None:
		if label_w_per <= 0 or label_w_per > 100:
			failed_validations["labelWPer"] = "Invalid input (labelWPer >= 0)"
		wallpaper.label_w_per = label_w_per

	label_h_per: float | None = payload.get("labelHPer")
	if label_h_per is not None:
		if label_h_per <= 0 or label_h_per > 100:
			failed_validations["labelHPer"] = "Invalid input (labelHPer >= 0)"
		wallpaper.label_h_per = label_h_per

	color: str | None = payload.get("color")
	if color is not None:
		if color.upper() not in supported_colors:
			failed_validations["color"] = "Invalid input (Unsupported color)"
		wallpaper.color = color.upper()

	shadow: int | None = payload.get("shadow")
	if shadow is not None:
		if shadow.upper() not in supported_colors:
			failed_validations["shadow"] = "Invalid input (Unsupported color)"
		wallpaper.shadow = shadow.upper()

	if len(failed_validations.values()) > 0:
		db.session.rollback();
		api_abort(ErrorCode.VALIDATION_ERROR, errors=failed_validations)

	wallpaper.updated_at = datetime.now(timezone("Asia/Singapore"))

	try:
		db.session.commit()
	except Exception as ex:
		db.session.rollback()
		logger.error(f"DB commit failed: {ex}")
		api_abort(ErrorCode.DATABASE_ERROR)

	logger.info(f"Wallpaper {wallpaper_id=} updated")


def get_wallpaper_name(wallpaper_id: int | None) -> str:
	model: WallpaperModel | None = db.session.get(WallpaperModel, wallpaper_id)
	if model is None:
		api_abort(ErrorCode.WALLPAPER_NOT_FOUND)
		
	file_name: str = model.file_name
	file_path: str = os.path.join(DIR_APP_UPLOAD, f"{file_name}")
	if not os.path.isfile(file_path):
		api_abort(ErrorCode.WALLPAPER_NOT_FOUND, detail="Wallpaper image file not found")

	return file_name


def get_wallpapers(user_id: int, device_id:int) -> list[dict]:
	select_wallpaper_ids_stmt = select(WallpaperOwnershipModel.wallpaper_id).where(
		and_(
			WallpaperOwnershipModel.user_id == user_id,
			WallpaperOwnershipModel.device_id == device_id
		))
	
	wallpaper_ids: Sequence[int] = db.session.scalars(select_wallpaper_ids_stmt).all()

	select_wallpaper_stmt = select(WallpaperModel).where(WallpaperModel.id.in_(wallpaper_ids))
	wallpapers: Sequence[WallpaperModel] = db.session.scalars(select_wallpaper_stmt).all()	
	
	return [wp.to_dict() for wp in wallpapers]
