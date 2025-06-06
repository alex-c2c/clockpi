import os

from flask import Blueprint, current_app, flash, redirect, request, url_for
from threading import Thread

from flask_restx import Namespace, Resource
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from app import api_v1
from app.consts import *
from app.enums import TimeMode, TextColor
from app.auth.logic import apikey_required, login_required
from app.queue.logic import move_to_first

from . import logger
from .consts import *
from .logic import add, remove, update


bp: Blueprint = Blueprint("wallpaper", __name__, url_prefix="/wallpaper")
ns: Namespace = api_v1.namespace("wallpaper", description="Wallpaper operations")


"""
API
"""


@ns.route("/")
class WallpaperListRes(Resource):
	@apikey_required
	def post(self) -> dict:
		# Check for file in request.files
		if "file" not in request.files:
			api_v1.abort(400, "Missing file(s)")

		files: list[FileStorage] = request.files.getlist("file")

		# Validate files first
		for file in files:
			if file.filename == "":
				api_v1.abort(400, "Invalid file name")

			if (
				"." not in file.filename
				or file.filename.rsplit(".", 1)[1].lower() not in ALLOWED_EXTENSIONS
			):
				api_v1.abort(400, "Invalid file extension")

		# Process files
		for file in files:
			# secure file name
			filename: str = secure_filename(file.filename)

			# save file to temp dir
			# TODO: improve location of "uploaded" files so that it doesn't get
			# overwritten by someone else uploading the files with same file name at the same time
			if not os.path.isdir(DIR_TMP_UPLOAD):
				os.mkdir(DIR_TMP_UPLOAD)

			temp_path: str = os.path.join(
				DIR_TMP_UPLOAD, filename
			)
			file.save(temp_path)

			t: Thread = Thread(
				target=add,
				args=(
					current_app.app_context(),
					filename,
				),
			)
			t.start()

		return "", 204


@ns.route("/<int:id>")
@api_v1.doc(responses={400: "Wallpaper ID not found"}, params={"id": "Wallpaper ID"})
class WallpaperRes(Resource):
	@apikey_required
	def delete(self, id: int) -> dict:
		result: int = remove(id)

		if result == 0:
			return "", 204

		elif result == ERR_WALLPAPER_INVALID_ID:
			api_v1.abort(400, "Wallpaper ID not found")

		else:
			return api_v1.abort(400, "Bad request")

	@apikey_required
	def patch(self, id: int) -> dict:
		d: dict = request.get_json()
		logger.info(f"{d=}")

		def try_get_bool(day: str) -> bool | None:
			return (
				d.get(day)
				if d.get(day) is not None and type(d.get(day)) is bool
				else None
			)

		def try_get_int(key: str) -> int | None:
			return (
				d.get(key)
				if d.get(key) is not None and type(d.get(key)) is int
				else None
			)

		is_select: bool | None = try_get_bool("select")
		# is_delete: bool = request.form.get("delete") is not None
		mode: int | None = try_get_int("mode")
		color: int | None = try_get_int("color")
		shadow: int | None = try_get_int("shadow")
		logger.info(f"update {id=} {mode=} {color=} {shadow=} {is_select=}")

		result: int = update(id, mode, color, shadow)
		if result == 0:
			if is_select is not None and is_select:
				move_to_first(id)

			return "", 204

		elif result == ERR_WALLPAPER_INVALID_DATA:
			api_v1.abort(400, "Invalid data")

		elif result == ERR_WALLPAPER_INVALID_ID:
			api_v1.abort(400, "Invalid ID")

		else:
			return api_v1.abort(400, "Bad request")


"""
Blueprints
"""


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
			if not os.path.isdir(DIR_TMP_UPLOAD):
				os.mkdir(DIR_TMP_UPLOAD)

			temp_path: str = os.path.join(
				DIR_TMP_UPLOAD, file_name
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
