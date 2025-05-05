import hashlib
import os
import shutil

from clockpi.consts import *
import clockpi.db as db
import clockpi.image as image
import clockpi.queue as queue
import clockpi.redis_controller as redis

from datetime import datetime
from flask import current_app
from flask.ctx import AppContext

from logging import Logger, getLogger


logger: Logger = getLogger(__name__)


def epd_update() -> None:
	logger.debug(f"epd_update")

	draw_grids: bool = True if redis.rget(R_SETTINGS_DRAW_GRIDS, "1") == "1" else False
	image_queue: tuple[int] = queue.get_queue()

	if len(image_queue) == 0:
		return

	image = db.get_image(image_queue[0])
	hash: str = image["hash"] if image is not None else ""

	if len(hash) > 0:
		file_path: str = os.path.join(
			current_app.config["DIR_APP_UPLOAD"], f"{hash}.bmp"
		)
		if not os.path.isfile(file_path):
			file_path = ""

	time: str = f"{datetime.now().hour:02d}:{datetime.now().minute:02d}"
	mode: str = image["mode"]
	color: str = image["color"]
	shadow: str = image["shadow"]

	redis.rpublish(
		f"{R_MSG_DRAW}^{file_path}^{time}^{mode}^{color}^{shadow}^{'1' if draw_grids else '0'}"
	)


def epd_clear() -> None:
	logger.debug(f"epd_clear")
	redis.rpublish(R_MSG_CLEAR)


def process_uploaded_file(app_context: AppContext, file_name: str) -> int:
	app_context.push()

	logger.info(f"Processing {file_name=}")
	temp_path: str = os.path.join(current_app.config["DIR_TMP_UPLOAD"], file_name)

	# validate image
	if not image.validate_image(temp_path):
		os.remove(temp_path)
		return ERR_UPLOAD_INVALID_IMAGE

	# process image
	if not os.path.isdir(current_app.config["DIR_TMP_PROCESSED"]):
		os.mkdir(current_app.config["DIR_TMP_PROCESSED"])

	processed_path: str = os.path.join(
		current_app.config["DIR_TMP_PROCESSED"], file_name
	)
	process_result: bool = image.procsess_image(
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
		image_id: int = db.add_image(filename_no_ext, hash, filesize)

		# Append to image queue
		queue.append_to_queue(image_id)

	except OSError as error:
		return ERR_UPLOAD_SAVE

	return 0


def remove_image(id: int) -> None:
	image = db.get_image(id)
	if image is None:
		return

	hash: str = image["hash"]
	file_path: str = os.path.join(current_app.config["DIR_APP_UPLOAD"], f"{hash}.bmp")
	logger.info(msg=f"Deleting {file_path=}")
	if os.path.isfile(file_path):
		os.remove(file_path)

	db.remove_image(id)
	queue.remove_id(id)
