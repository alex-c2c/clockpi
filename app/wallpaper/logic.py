import hashlib
import os
import shutil
from typing import Sequence
import numpy as np

from logging import Logger, getLogger
from PIL.Image import Image
from PIL import Image as Img
from PIL import ImageFilter

from sqlalchemy import select
from flask.ctx import AppContext

from app import db
from app.consts import *
from app.epd.consts import *
from app.queue.logic import append_to_queue, remove_from_queue

from . import ns
from .models import WallpaperModel

logger: Logger = getLogger(__name__)

"""""
LOGIC
"""""

def crop(img: Image, size: tuple[int, int]) -> Image:
	l: float = (img.width - size[0]) * 0.5
	r: float = l + size[0]
	t: float = (img.height - size[1]) * 0.5
	b: float = t + size[1]

	return img.crop((l, t, r, b))


def get_new_val(old_val, nc):
	return np.round(old_val * (nc - 1)) / (nc - 1)


# Floyd-Steinberg dither the image img into a palette with nc colours per channel.
# https://scipython.com/blog/floyd-steinberg-dithering/
def fs_dither(img: Image, nc: int) -> Image:
	h: int = img.height
	w: int = img.width
	arr = np.array(img, dtype=float) / 255

	for ir in range(h):
		for ic in range(w):
			# NB need to copy here for RGB arrays otherwise err will be (0,0,0)!
			old_val = arr[ir, ic].copy()
			new_val = get_new_val(old_val, nc)
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
def palette_reduce(img: Image, nc: int) -> Image:
	arr = np.array(img, dtype=float) / 255
	arr = get_new_val(arr, nc)

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
	image_size: tuple[int, int],
	image_pos: tuple[int, int],
	nc: int,
	del_src: bool = True,
) -> bool:
	try:
		canvas: Image = Img.new("RGB", canvas_size)
		bg: Image = Img.open(file_path)
		fg: Image = Img.open(file_path)

		w: int = bg.width
		h: int = bg.height

		# Resize
		bg_r: float = max(canvas_size[0] / w, canvas_size[1] / h)
		bg.thumbnail((w * bg_r, h * bg_r), Img.Resampling.LANCZOS)

		fg_r: float = max(image_size[0] / w, image_size[1] / h)
		fg.thumbnail((w * fg_r, h * fg_r), Img.Resampling.LANCZOS)
	
		# Apply gaussian blur to bg
		bg = bg.filter(ImageFilter.GaussianBlur(radius=5))

		# Crop
		bg = crop(bg, canvas_size)
		fg = crop(fg, image_size)

		# Paste bg & fg to canvas
		canvas.paste(bg, (0, 0))
		canvas.paste(fg, image_pos)

		# Apply fyold steinburg dithering
		canvas = fs_dither(canvas, nc)

		# Reduce palette color
		canvas = palette_reduce(canvas, nc)

		# Save file
		canvas.save(dest_path)

		if del_src:
			os.remove(file_path)

		return True

	except IOError as error:
		logger.error(f"process_image: {error}")
		return False


def create_wallpaper(app_context: AppContext, file_name: str) -> None:
	logger.info(f"Attempting to process {file_name} and create new wallpaper")
	
	app_context.push()

	temp_path: str = os.path.join(DIR_TMP_UPLOAD, file_name)

	# validate image
	if not _validate_image(temp_path):
		os.remove(temp_path)
		logger.error(f"Uploaded file is invalid")
		ns.abort(400, "Uploaded file is invalid")
		return
		
	# process image
	if not os.path.isdir(DIR_TMP_PROCESSED):
		os.mkdir(DIR_TMP_PROCESSED)

	processed_path: str = os.path.join(
		DIR_TMP_PROCESSED, file_name
	)
	process_result: bool = process_image(
		file_path=temp_path,
		dest_path=processed_path,
		canvas_size=(EPD_WIDTH, EPD_WIDTH),
		image_size=(EPD_WIDTH, EPD_WIDTH),
		image_pos=(0, 0),
		nc=EPD_NC
	)

	if not process_result:
		if os.path.isfile(temp_path):
			os.remove(temp_path)
		if os.path.isfile(processed_path):
			os.remove(processed_path)
		logger.error(f"Unable to proccess image")
		ns.abort(500, "Unable to process image")
		return

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
		logger.error(f"Unable to obtain file hash due to {error}")
		ns.abort(500, "Unable to obtain file hash")
		return

	# copy processed image to upload dir
	try:
		hashname: str = f"{hash}.bmp"
		dest_path: str = os.path.join(DIR_APP_UPLOAD, hashname)
		shutil.copy2(processed_path, dest_path)
		os.remove(processed_path)

	except OSError as error:
		if os.path.isfile(temp_path):
			os.remove(temp_path)
		if os.path.isfile(processed_path):
			os.remove(processed_path)
		logger.error(f"Unable to copy file due to {error}")
		ns.abort(500, "Unable to copy file")
		return

	# Save upload entry to DB
	try:
		filename_no_ext: str = file_name.rsplit(".", 1)[0]
		filesize: int = os.path.getsize(dest_path)

		# Insert to DB
		new_model: WallpaperModel = WallpaperModel(filename_no_ext, hash, filesize)
		db.session.add(new_model)
		db.session.commit()

		# Append to image queue
		append_to_queue(new_model.id)

	except OSError as error:
		logger.error(f"Unable to create new wallpaper model due to {error}")
		ns.abort(500, "Unable to create new wallpaper model")
		return
	
	logger.info(f"Processed image and created new wallpaper model")


def remove_wallpaper(id: int) -> None:
	logger.info(msg=f"Attempting to delete wallpaper {id=}")

	model: WallpaperModel | None = db.session.get(WallpaperModel, id)
	if model is None:
		ns.abort(404, "Invalid or missing ID")
		return
		
	hash: str = model.hash
	file_path: str = os.path.join(DIR_APP_UPLOAD, f"{hash}.bmp")

	if not os.path.isfile(file_path):
		ns.abort(404, "Invalid or missing file")
		return
			
	try:
		db.session.delete(model)
		db.session.commit()
	except Exception as e:
		logger.error(f"Unable to delete wallpaper model due to {e}")
		ns.abort(500, "Internal Server Error")
		return
		
	remove_from_queue(id)
		
	os.remove(file_path)

	logger.info(f"Deleted wallpaper {id=}")


def update_wallpaper(id: int, data: dict) -> None:
	logger.info(f"Attempting to update wallpaper {id=}")
	
	model: WallpaperModel | None = db.session.get(WallpaperModel, id)
	if model is None:
		ns.abort(404, "Invalid or missing ID")
		return
	
	mode: int | None = data.get("mode")
	if mode is not None:
		if mode < TIMEMODE_OFF or mode > TIMEMODE_FULL_3:
			ns.abort(400, "Invalid mode")
			return
		model.mode = mode
	
	color: str | None = data.get("color")
	if color is not None:
		if color.upper() not in Color:
			logger.error(f"Invalid color {color}")
			ns.abort(400, "Invalid color")
			return
		model.color = Color[color.upper()]
		
	shadow: int | None = data.get("shadow")
	if shadow is not None:
		if shadow.upper() not in Color:
			logger.error(f"Invalid shadow: {shadow}")
			ns.abort(400, "Invalid shadow")
			return
		model.shadow = Color[shadow.upper()]
		
	try:
		db.session.commit()
	except Exception as e:
		logger.error(f"Unable to update wallpaper due to {e}")
		ns.abort(500, "Internal Server Error")
		return
	
	logger.info(f"Wallpaper {id=} updated")
	

def get_wallpaper_name(id: int) -> str:
	model: WallpaperModel | None = db.session.get(WallpaperModel, id)
	if model is None:
		ns.abort(404, "Invalid or missing ID")
		return ""
		
	file_path: str = os.path.join(DIR_APP_UPLOAD, f"{model.hash}.bmp")
	if not os.path.isfile(file_path):
		ns.abort(404, "Invalid or missing file")
		return ""
		
	return f"{model.hash}.bmp"


def get_wallpapers() -> list[dict]:
	data: Sequence[WallpaperModel] = db.session.scalars(select(WallpaperModel)).all()
	
	wallpapers: list[dict] = []
	for row in data:
		wallpapers.append(row.to_dict())
		
	return wallpapers
