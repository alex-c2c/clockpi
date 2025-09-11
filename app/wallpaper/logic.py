import hashlib
import os
import numpy as np
import shutil

from datetime import datetime
from logging import Logger, getLogger

from PIL.Image import Image
from PIL import Image as Img
from PIL import ImageFilter

from pytz import timezone
from sqlalchemy import delete, select
from flask.ctx import AppContext

from app import db
from app.consts import *
from app.device.logic import can_access_device
from app.device.models import DeviceModel
from app.epd7in3e.consts import *
from app.device.logic.queue import append_to_queue, remove_from_queue
from app.lib.errors import api_abort, ErrorCode

from .models import WallpaperModel

logger: Logger = getLogger(__name__)

"""""
LOGIC
"""""


def _crop(img: Image, size: tuple[int, int]) -> Image:
	l: float = (img.width - size[0]) * 0.5
	r: float = l + size[0]
	t: float = (img.height - size[1]) * 0.5
	b: float = t + size[1]

	return img.crop((l, t, r, b))


def _get_new_val(old_val, nc):
	return np.round(old_val * (nc - 1)) / (nc - 1)


# Floyd-Steinberg dither the image img into a palette with nc colours per channel.
# https://scipython.com/blog/floyd-steinberg-dithering/
def _fs_dither(img: Image, nc: int) -> Image:
	h: int = img.height
	w: int = img.width
	arr = np.array(img, dtype=float) / 255

	for ir in range(h):
		for ic in range(w):
			# NB need to copy here for RGB arrays otherwise err will be (0,0,0)!
			old_val = arr[ir, ic].copy()
			new_val = _get_new_val(old_val, nc)
			arr[ir, ic] = new_val
			err = old_val - new_val
			# In this simple example, we will just ignore the border pixels.
			if ic < w - 1:
				arr[ir, ic + 1] += err * 7 / 16
			if ir < h - 1:
				if ic > 0:
					arr[ir + 1, ic - 1] += err * 3 / 16
				arr[ir + 1, ic] += err * 5 / 16
				if ic < w - 1:
					arr[ir + 1, ic + 1] += err / 16

	carr = np.array(arr / np.max(arr, axis=(0, 1)) * 255, dtype=np.uint8)
	return Img.fromarray(carr)


# Simple palette reduction without dithering.
def _palette_reduce(img: Image, nc: int) -> Image:
	arr = np.array(img, dtype=float) / 255
	arr = _get_new_val(arr, nc)

	carr = np.array(arr / np.max(arr) * 255, dtype=np.uint8)
	return Img.fromarray(carr)


def _validate_image(file_path: str) -> bool:
	try:
		img: Image = Img.open(file_path)
		img.verify()
		return True
	except Exception as e:
		logger.error(f"_validate_image: {e}")
		return False


def process_image(
	file_path: str,
	dest_path: str,
	canvas_size: tuple[int, int],
	image_scale: float,
	image_offset: tuple[int, int],
	nc: int,
	del_src: bool = True,
) -> bool:
	try:
		canvas: Image = Img.new("RGB", canvas_size)
		bg: Image = Img.open(file_path)
		fg: Image = Img.open(file_path)

		w: int = bg.width
		h: int = bg.height

		# Resize bg to fill the entire canvas
		# According to orientation
		bg_r: float = max(canvas_size[0] / w, canvas_size[1] / h)
		bg.thumbnail((w * bg_r, h * bg_r), Img.Resampling.LANCZOS)

		# Resize foreground image to user specified percentage scale
		# image_scale represents the the image width as a percent of canvas width (fixed size)
		true_scale: float = (canvas_size[0] * image_scale) / fg.width
		
		fg.thumbnail(
			(int(fg.width * true_scale), int(fg.height * true_scale)),
			Img.Resampling.LANCZOS,
		)

		# Apply gaussian blur to bg
		bg = bg.filter(ImageFilter.GaussianBlur(radius=4))

		# Paste bg to canvas
		# Centralize it vertically or horizontally depending on orientation
		if canvas.width < canvas.height:
			# vertical
			bg_offset_y: int = int((bg.height - canvas.height) * 0.5)
			canvas.paste(bg, (0, -bg_offset_y))
		else:
			# horizontal
			bg_offset_x: int = int((bg.width - canvas.width) * 0.5)
			canvas.paste(bg, (-bg_offset_x, 0))

		# Paste fg to canvas
		# Use user specified offsets
		canvas.paste(fg, image_offset)

		# Apply fyold steinburg dithering
		canvas = _fs_dither(canvas, nc)

		# Reduce palette color
		canvas = _palette_reduce(canvas, nc)

		# Save file
		canvas.save(dest_path)

		if del_src:
			os.remove(file_path)

		return True

	except IOError as error:
		logger.error(f"process_image: {error}")
		return False


def create_wallpaper(
	app_context: AppContext,
	file_name: str,
	user_id:int,
	device_id: int,
	img_scale_per: float,
	x_pos_per: float,
	y_pos_per: float
) -> None:
	logger.info(f"Attempting to process \
		{file_name} for \
		{user_id=} {device_id=} - \
		{img_scale_per=} {x_pos_per=} {y_pos_per=}"
	)

	app_context.push()
	
	device: DeviceModel | None = db.session.get(DeviceModel, device_id)
	if device is None:
		api_abort(ErrorCode.INVALID_DEPENDENCY, detail="Device not found")

	if not can_access_device(user_id, device_id):
		api_abort(ErrorCode.INVALID_DEPENDENCY, detail="Unable to access device")

	temp_path: str = os.path.join(DIR_TMP_UPLOAD, file_name)

	# validate image
	if not _validate_image(temp_path):
		os.remove(temp_path)
		logger.error(f"Invalid image file")
		api_abort(ErrorCode.UNPROCESSABLE_ENTITY)

	# process image
	if not os.path.isdir(DIR_TMP_PROCESSED):
		os.mkdir(DIR_TMP_PROCESSED)

	processed_path: str = os.path.join(DIR_TMP_PROCESSED, file_name)
	process_result: bool = process_image(
		file_path=temp_path,
		dest_path=processed_path,
		canvas_size=(device.width, device.height),
		image_scale=img_scale_per,
		image_offset=(int(device.width * x_pos_per), int(device.height * y_pos_per)),
		nc=EPD_NC,
	)

	if not process_result:
		if os.path.isfile(temp_path):
			os.remove(temp_path)
		if os.path.isfile(processed_path):
			os.remove(processed_path)
		logger.error(f"Unable to proccess image")
		api_abort(ErrorCode.INTERNAL_SERVER_ERROR)

	# get hash of processed image
	try:
		h = hashlib.sha256()
		with open(processed_path, "rb") as f:
			while True:
				chunk = f.read(h.block_size)
				if not chunk:
					break
				h.update(chunk)
		hash: str = h.hexdigest()

	except OSError as error:
		if os.path.isfile(temp_path):
			os.remove(temp_path)
		if os.path.isfile(processed_path):
			os.remove(processed_path)
		logger.error(f"Unable to obtain file hash: {error}")
		api_abort(ErrorCode.INTERNAL_SERVER_ERROR)

	# copy processed image to upload dir
	try:
		new_file_name: str = f"{hash[0:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bmp"
		dest_path: str = os.path.join(DIR_APP_UPLOAD, new_file_name)
		shutil.copy2(processed_path, dest_path)
		os.remove(processed_path)

	except OSError as error:
		if os.path.isfile(temp_path):
			os.remove(temp_path)
		if os.path.isfile(processed_path):
			os.remove(processed_path)
		logger.error(f"Unable to copy file due to {error}")
		api_abort(ErrorCode.INTERNAL_SERVER_ERROR)
		return

	# Save upload entry to DB
	try:
		name: str = file_name.rsplit(".", 1)[0]
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

	model: WallpaperModel | None = db.session.get(WallpaperModel, wallpaper_id)
	if model is None:
		api_abort(ErrorCode.WALLPAPER_NOT_FOUND)
		
	if not can_access_device(user_id, model.device_id):
		api_abort(ErrorCode.FORBIDDEN)

	file_name: str = model.file_name
	file_path: str = os.path.join(DIR_APP_UPLOAD, file_name)

	if os.path.isfile(file_path):
		os.remove(file_path)
	else:
		logger.error(f"Unable to find wallpaper file {file_path}")
		
	try:
		db.session.delete(model)
		db.session.commit()
	except Exception as e:
		logger.error(f"Unable to delete wallpaper model due to {e}")
		api_abort(ErrorCode.INTERNAL_SERVER_ERROR)

	remove_from_queue(user_id, model.device_id, wallpaper_id)

	os.remove(file_path)

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
		api_abort(ErrorCode.VALIDATION_ERROR, fields=failed_validations)

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
