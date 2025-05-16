import os

from logging import Logger, getLogger
from flask import Blueprint, current_app, flash, redirect, request, url_for
from threading import Thread

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from app.auth.logic import login_required
from app.consts import *
from app.queue.logic import move_to_first
from app.wallpaper.logic import add, remove, update


bp: Blueprint = Blueprint("wallpaper", __name__, url_prefix="/wallpaper")
logger: Logger = getLogger(__name__)


@bp.route("/upload", methods=["POST"])
@login_required
def view_upload():
	if request.method == "POST" and "file" in request.files:
		if "file" not in request.files:
			flash("No file part")
			return redirect(url_for("main.view_test"))

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
				target=add,
				args=(
					current_app.app_context(),
					file_name,
				),
			)
			t.start()

	return redirect(url_for("main.view_test"))


@bp.route("/update/<int:id>", methods=["POST"])
@login_required
def view_update(id: int):
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
			remove(id)

		else:
			update(id, mode, color, shadow)

			if is_select:
				move_to_first(id)

	return redirect(url_for(endpoint="main.view_test"))
