import hashlib
import os
import shutil
from threading import Thread
import numpy as np

from app import db, queue
from app.auth.logic import login_required
from app.consts import *
from app.models import WallpaperModel

from flask import Blueprint, current_app, flash, redirect, request, url_for
from flask.ctx import AppContext
from PIL import Image as Image
from logging import Logger, getLogger
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


bp: Blueprint = Blueprint("wallpaper", __name__, url_prefix="/wallpaper")
logger: Logger = getLogger(__name__)


def _crop(img: Image, w: int, h: int) -> Image:
	l: float = (img.width - w) * 0.5
	r: float = l + w
	t: float = (img.height - h) * 0.5
	b: float = t + h

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
	return Image.fromarray(carr)


# Simple palette reduction without dithering.
def _palette_reduce(img: Image, nc: int) -> Image:
	arr = np.array(img, dtype=float) / 255
	arr = _get_new_val(arr, nc)

	carr = np.array(arr / np.max(arr) * 255, dtype=np.uint8)
	return Image.fromarray(carr)


def _validate_image(file_path: str) -> bool:
	try:
		img: Image = Image.open(file_path)
		img.verify()
		return True
	except (IOError, SyntaxError):
		return False


def _process_image(
	file_path: str,
	dest_path: str,
	to_width: int,
	to_height: int,
	nc: int,
	del_src: bool = True,
) -> bool:
	try:
		img: Image = Image.open(file_path)
		w: int = img.width
		h: int = img.height

		# resize
		r: float = max(to_width / w, to_height / h)
		img.thumbnail((w * r, h * r), Image.Resampling.LANCZOS)

		# _crop
		img: Image = _crop(img, to_width, to_height)

		# Apply fyold steinburg dithering
		img = _fs_dither(img, nc)

		# Reduce palette color
		img = _palette_reduce(img, nc)

		# Save file
		img.save(dest_path)

		if del_src:
			os.remove(file_path)

		return True

	except IOError as error:
		logger.error(error)
		return False


def _add(app_context: AppContext, file_name: str) -> int:
	app_context.push()

	logger.info(f"Processing {file_name=}")
	temp_path: str = os.path.join(current_app.config["DIR_TMP_UPLOAD"], file_name)

	# validate image
	if not _validate_image(temp_path):
		os.remove(temp_path)
		return ERR_UPLOAD_INVALID_IMAGE

	# process image
	if not os.path.isdir(current_app.config["DIR_TMP_PROCESSED"]):
		os.mkdir(current_app.config["DIR_TMP_PROCESSED"])

	processed_path: str = os.path.join(
		current_app.config["DIR_TMP_PROCESSED"], file_name
	)
	process_result: bool = _process_image(
		temp_path, processed_path, EPD_WIDTH, EPD_HEIGHT, EPD_NC
	)

	if not process_result:
		if os.path.isfile(temp_path):
			os.remove(temp_path)
		if os.path.isfile(processed_path):
			os.remove(processed_path)
		return ERR_UPLOAD_POST_PROC

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
		return ERR_UPLOAD_HASH

	# copy processed image to upload dir
	try:
		hashname: str = f"{hash}.bmp"
		dest_path: str = os.path.join(current_app.config["DIR_APP_UPLOAD"], hashname)
		shutil.copy2(processed_path, dest_path)
		os.remove(processed_path)

	except OSError as error:
		if os.path.isfile(temp_path):
			os.remove(temp_path)
		if os.path.isfile(processed_path):
			os.remove(processed_path)
		return ERR_UPLOAD_COPY

	# Save upload entry to DB
	try:
		filename_no_ext: str = file_name.rsplit(".", 1)[0]
		filesize: int = os.path.getsize(dest_path)

		# Insert to DB
		new_model: WallpaperModel = WallpaperModel(filename_no_ext, hash, filesize)
		db.session.add(new_model)
		db.session.commit()

		# Append to image queue
		queue.append_to_queue(new_model.id)

	except OSError as error:
		return ERR_UPLOAD_SAVE

	return 0


def _remove(id: int) -> None:
	model: WallpaperModel = WallpaperModel.query.get(id)

	if model is None:
		return

	hash: str = model.hash
	file_path: str = os.path.join(current_app.config["DIR_APP_UPLOAD"], f"{hash}.bmp")
	logger.info(msg=f"Deleting {file_path=}")
	if os.path.isfile(file_path):
		os.remove(file_path)

	db.session.delete(model)
	db.session.commit()

	queue.remove_id(id)


def _update(id: int, mode: int, color: int, shadow: int) -> None:
	model: WallpaperModel = WallpaperModel.query.get(id)
	if model is not None:
		model.mode = mode
		model.color = color
		model.shadow = shadow
		db.session.commit()


@bp.route("/upload", methods=["POST"])
@login_required
def upload():
	if request.method == "POST" and "file" in request.files:
		if "file" not in request.files:
			flash("No file part")
			return redirect(url_for("clock.test"))

		files: list[FileStorage] = request.files.getlist("file")

		logger.info(f"upload {len(files)=}")

		for file in files:
			# secure file name
			file_name = secure_filename(file.filename)

			if file_name == "":
				flash("No file part")
				continue

			if (
				"." not in file_name
				or file_name.rsplit(".", 1)[1].lower() not in ALLOWED_EXTENSIONS
			):
				flash(f"Uploaded image {file_name=} with invalid extension")
				continue

			# save file to temp dir
			# TODO: improve location of "uploaded" files so that it doesn't get
			# overwritten by someone else uploading the files with same file name at the same time
			if not os.path.isdir(current_app.config["DIR_TMP_UPLOAD"]):
				os.mkdir(current_app.config["DIR_TMP_UPLOAD"])

			temp_path: str = os.path.join(
				current_app.config["DIR_TMP_UPLOAD"], file_name
			)
			file.save(temp_path)

			t: Thread = Thread(
				target=_add,
				args=(
					current_app.app_context(),
					file_name,
				),
			)
			t.start()

	return redirect(url_for("clock.test"))


@bp.route("/update/<int:id>", methods=["POST"])
@login_required
def update(id: int):
	if request.method == "POST":
		is_select: bool = request.form.get("select") is not None
		is_delete: bool = request.form.get("delete") is not None
		mode: int = int(request.form.get("mode", str(TimeMode.FULL_3.value)))
		color: int = int(request.form.get("color", str(TextColor.WHITE.value)))
		shadow: int = int(request.form.get("shadow", str(TextColor.BLACK.value)))
		logger.info(
			f"update {id=} {mode=} {color=} {shadow=} {is_select=} {is_delete=}"
		)

		if is_delete:
			_remove(id)

		else:
			_update(id, mode, color, shadow)

			if is_select:
				queue.move_to_first(id)

	return redirect(url_for(endpoint="clock.test"))
