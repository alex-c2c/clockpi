import queue
import os

from app import redis_controller, db, logic, queue, wallpaper
from datetime import datetime
from logging import Logger, getLogger
from threading import Thread
from flask import (
	Blueprint,
	current_app,
	flash,
	redirect,
	render_template,
	request,
	url_for,
)
from app.auth import login_required
from app.consts import *

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from app.models import WallpaperModel


bp = Blueprint("clockpi", __name__)
logger: Logger = getLogger(__name__)


def allowed_file(filename) -> bool:
	return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/", methods=["GET"])
@login_required
def index():
	return render_template(("clockpi/index.html"))


@bp.route("/upload_file", methods=["POST"])
@login_required
def upload_file():
	if request.method == "POST" and "file" in request.files:
		if "file" not in request.files:
			flash("No file part")
			return redirect(url_for("clockpi.test"))

		files: list[FileStorage] = request.files.getlist("file")

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
				target=logic.process_uploaded_file,
				args=(
					current_app.app_context(),
					file_name,
				),
			)
			t.start()

	return redirect(url_for("clockpi.test"))


@bp.route("/test", methods=["GET"])
@login_required
def test():
	# Get settings from Redis
	draw_grids: bool = redis_controller.get_draw_grids()
	epd_busy: bool = redis_controller.get_epd_busy()

	# Get all wallpapers
	wallpapers: list = WallpaperModel.query.order_by(WallpaperModel.id).all()

	# Get wallpaper queue
	wallpaper_queue: list[int] = queue.get_queue()

	# Text Color
	text_color: dict[str, int] = TEXT_COLOR_DICT

	# Time Modes
	mode: dict[str, int] = TIME_MODE_DICT

	# Sleep Schedules
	now_hr: int = datetime.now().hour
	now_min: int = datetime.now().minute

	return render_template(
		"clockpi/test.html",
		draw_grids=draw_grids,
		epd_busy=epd_busy,
		wallpapers=wallpapers,
		wallpaper_queue=wallpaper_queue,
		text_color=text_color,
		mode=mode,
	)


@bp.route("/shuffle", methods=["GET"])
@login_required
def shuffle():
	queue.shuffle_queue()

	return redirect(location=url_for("clockpi.test"))


@bp.route("/clear", methods=["GET"])
@login_required
def clear():
	logic.epd_clear()

	return redirect(location=url_for("clockpi.test"))


@bp.route("/refresh", methods=["GET"])
@login_required
def refresh():
	logic.epd_update()

	return redirect(location=url_for("clockpi.test"))


@bp.route("/next", methods=["GET"])
@login_required
def next():
	queue.shift_next()

	return redirect(location=url_for("clockpi.test"))


@bp.route("/draw_grids", methods=["POST"])
@login_required
def set_draw_grids():
	if request.method == "POST":
		draw_grids: bool = request.form.get("draw_grids", "") == "true"

		logger.info(f"set draw grids {draw_grids=}")

		# Update Redis
		redis_controller.rset(R_SETTINGS_DRAW_GRIDS, "1" if draw_grids else "0")

	return redirect(url_for(endpoint="clockpi.test"))


@bp.route("/update/<int:id>", methods=["POST"])
@login_required
def update(id: int):
	if request.method == "POST":
		is_select: bool = request.form.get("select") is not None
		is_delete: bool = request.form.get("delete") is not None
		mode: int = int(request.form.get("mode", TimeMode.FULL_3))
		color: int = int(request.form.get("color", TextColor.NONE))
		shadow: int = int(request.form.get("shadow", TextColor.NONE))
		logger.info(
			f"update image {id=} {mode=} {color=} {shadow=} {is_select=} {is_delete=}"
		)

		if is_delete:
			logic.remove_image(id)

		else:
			model: WallpaperModel = WallpaperModel.query.get(id)
			if model is not None:
				model.mode = mode
				model.color = color
				model.shadow = shadow
				db.session.commit()

			if is_select:
				queue.move_to_first(id)

	return redirect(url_for(endpoint="clockpi.test"))


@bp.route("/select", methods=["POST"])
@login_required
def select():
	if request.method == "POST":
		if request.form.get("id") is not None:
			image_id: int = int(request.form.get("id"))
			queue.move_to_first(image_id)

	return redirect(url_for(endpoint="clockpi.test"))


@bp.route("/delete", methods=["POST"])
@login_required
def delete():
	if request.method == "POST":
		if request.form.get("id") is not None:
			image_id: int = int(request.form.get("id"))
			logic.remove_image(image_id)

	return redirect(url_for(endpoint="clockpi.test"))
