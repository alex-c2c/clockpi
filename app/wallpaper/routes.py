import os
from logging import Logger, getLogger
from threading import Thread

from flask import current_app,request, send_from_directory
from flask_restx import Resource
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from app import api
from app.auth.logic import local_apikey_required, react_login_required
from app.consts import *
from app.epd.consts import *
from app.queue.logic import move_to_first, get_queue

from . import ns
from .consts import *
from .logic import add, remove, update, get_wallpaper_name

logger: Logger = getLogger(__name__)


"""
API
"""


@ns.route("/upload")
class UploadRes(Resource):
	@react_login_required
	def post(self) -> dict:
		# Check for file in request.files
		if "file" not in request.files:
			api.abort(400, "Missing file(s)")

		files: list[FileStorage] = request.files.getlist("file")

		# Validate files first
		for file in files:
			if file.filename == "":
				api.abort(400, "Invalid file name")

			if (
				"." not in file.filename
				or file.filename.rsplit(".", 1)[1].lower() not in ALLOWED_EXTENSIONS
			):
				api.abort(400, "Invalid file extension")

		# Process files
		for file in files:
			# secure file name
			filename: str = secure_filename(file.filename)

			# save file to temp dir
			# TODO: improve location of "uploaded" files so that it doesn't get
			# overwritten by someone else uploading the files with same file name at the same time
			if not os.path.isdir(DIR_TMP_UPLOAD):
				os.mkdir(DIR_TMP_UPLOAD)

			temp_path: str = os.path.join(DIR_TMP_UPLOAD, filename)
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


@ns.route("/file/<int:id>")
@api.doc(responses={400: "Bad Request", 404: "Wallpaper ID not found"}, params={"id": "Wallpaper ID"})
class FileRes(Resource):
    @local_apikey_required
    def get(self, id: int) -> dict:
        file_name, result = get_wallpaper_name(id)
        if result == 0:
            return send_from_directory(DIR_APP_UPLOAD, file_name)
        elif result == ERR_WALLPAPER_INVALID_ID:
            api.abort(404, "Invalid wallpaper ID")
        else:
            api.abort(400, "Bad Request")


@ns.route("/file/current")
@api.doc(responses={400: "Bad Request", 404: "No wallpaper found"}, params={})
class FileCurrentRes(Resource):
    @local_apikey_required
    def get(self) -> dict:
        queue: list[int] = get_queue()
        if len(queue) == 0:
            api.abort(400)
        
        file_name, result = get_wallpaper_name(queue[0])
        if result == 0:
            return send_from_directory(DIR_APP_UPLOAD, file_name)
        elif result == ERR_WALLPAPER_INVALID_ID:
            api.abort(404, "Invalid wallpaper ID")
        else:
            api.abort(400, "Bad Request")
        
        
@ns.route("/<int:id>")
@api.doc(responses={400: "Bad Request", 404: "Wallpaper ID not found"}, params={"id": "Wallpaper ID"})
class Res(Resource):
	@react_login_required
	def delete(self, id: int) -> dict:
		result: int = remove(id)

		if result == 0:
			return "", 204
		elif result == ERR_WALLPAPER_INVALID_ID:
			api.abort(404, "Invalid wallpaper ID")
		else:
			return api.abort(400, "Bad Request")

	@react_login_required
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

		elif result == ERR_WALLPAPER_INVALID_PARAMS:
			api.abort(400, "Invalid wallpaper params")

		elif result == ERR_WALLPAPER_INVALID_ID:
			api.abort(400, "Invalid wallpaper ID")

		else:
			return api.abort(400, "Bad Request")
