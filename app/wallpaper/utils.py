import os
import numpy as np

from logging import Logger, getLogger

from PIL.Image import Image
from PIL import Image as Img
from PIL import ImageFilter

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.consts import *
from app.lib.errors import api_abort, ErrorCode
from app.wallpaper.consts import ALLOWED_EXTENSIONS


logger: Logger = getLogger(__name__)


def _crop(img: Image, size: tuple[int, int]) -> Image:
	l: float = (img.width - size[0]) * 0.5
	r: float = l + size[0]
	t: float = (img.height - size[1]) * 0.5
	b: float = t + size[1]

	return img.crop((l, t, r, b))


def get_new_val(old_val, nc):
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
def _palette_reduce(img: Image, nc: int) -> Image:
	arr = np.array(img, dtype=float) / 255
	arr = get_new_val(arr, nc)

	carr = np.array(arr / np.max(arr) * 255, dtype=np.uint8)
	return Img.fromarray(carr)


def validate_image(file_path: str) -> bool:
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


def save_upload_file(file: FileStorage | None) -> str:
	# Check for file in request.files
	if file is None:
		api_abort(ErrorCode.INVALID_INPUT, errors={"file":"This is a required property"})
	
	# Validate file first
	file_name: str | None = file.filename
	if file_name is None or len(file_name) == 0:
		api_abort(ErrorCode.INVALID_INPUT, errors={"file":"Invalid input"})
	
	if (
		"." not in file_name
		or file_name.rsplit(".", 1)[1].lower() not in ALLOWED_EXTENSIONS
	):
		api_abort(ErrorCode.UNSUPPORTED_MEDIA_TYPE, detail="Invalid file extension")
		
	# secure file name
	secured_file_name: str = secure_filename(file_name)

	# save file to temp dir
	# TODO: improve location of "uploaded" files so that it doesn't get
	# overwritten by someone else uploading the files with same file name at the same time
	if not os.path.isdir(DIR_TMP_UPLOAD):
		os.mkdir(DIR_TMP_UPLOAD)

	temp_path: str = os.path.join(DIR_TMP_UPLOAD, secured_file_name)
	file.save(temp_path)
	
	return secured_file_name


def is_valid_img_scale(value: str | None) -> str | None:
	if value is None:
		return "This is a required field"
		
	try:
		img_scale_per: float = float(value)
	except ValueError as e:
		return "Invalid input (float required)"
	
	return None
