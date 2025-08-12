import os
from logging import Logger, getLogger
from threading import Thread

from flask import current_app, request, send_from_directory
from flask_restx import Resource
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from app.auth.logic import admin_required, local_apikey_required, login_required
from app.consts import *
from app.epd.consts import *
from app.queue.logic import get_queue_model

from . import ns
from .consts import *
from .fields import *
from .logic import *

logger: Logger = getLogger(__name__)


"""
API
"""


@ns.route("/upload")
class UploadRes(Resource):
	@admin_required
	@ns.response(204, "")
	@ns.response(400, "Bad Request")
	@ns.response(400, "Invalid file name")
	@ns.response(400, "Invalid file extension")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(413, "Content too large")
	def post(self):
		# Check for file in request.files
		if "file" not in request.files:
			ns.abort(400, "Missing files")

		files: list[FileStorage] = request.files.getlist("file")

		# Validate files first
		for file in files:
			file_name: str | None = file.filename
			if file_name is None or len(file_name) == 0:
				ns.abort(400, "Invalid file name")
				return
			
			if (
				"." not in file_name
				or file_name.rsplit(".", 1)[1].lower() not in ALLOWED_EXTENSIONS
			):
				ns.abort(400, "Invalid file extension")
				return
		
			# secure file name
			secured_file_name: str = secure_filename(file_name)

			# save file to temp dir
			# TODO: improve location of "uploaded" files so that it doesn't get
			# overwritten by someone else uploading the files with same file name at the same time
			if not os.path.isdir(DIR_TMP_UPLOAD):
				os.mkdir(DIR_TMP_UPLOAD)

			temp_path: str = os.path.join(DIR_TMP_UPLOAD, secured_file_name)
			file.save(temp_path)

			t: Thread = Thread(
				target=create_wallpaper,
				args=(
					current_app.app_context(),
					secured_file_name,
				),
			)
			t.start()

		return "", 204


@ns.route("/file/<int:id>")
class FileRes(Resource):
	@local_apikey_required
	@ns.response(200, "Image file")
	@ns.response(401, "Authentication Error")
	@ns.response(404, "Invalid or missing ID")
	@ns.response(404, "Invalid or missing file")
	def get(self, id: int):
		file_name: str = get_wallpaper_name(id)
		return send_from_directory(DIR_APP_UPLOAD, file_name)


@ns.route("/file/current")
class FileCurrentRes(Resource):
	@local_apikey_required
	@ns.response(200, "Image file")
	@ns.response(401, "Authentication Error")
	@ns.response(404, "Invalid or missing ID")
	@ns.response(404, "Invalid or missing file")
	def get(self):
		queue: list[int] = get_queue_model().get_queue()
		logger.debug(f"current id: {queue}");
		if len(queue) == 0:
			ns.abort(404, "Invalid or missing ID")
					
		file_name: str= get_wallpaper_name(queue[0])
		return send_from_directory(DIR_APP_UPLOAD, file_name)


@ns.route("/")
class WallpaperListRes(Resource):
	@login_required
	@ns.response(200, "List of wallpaper fields")
	@ns.response(401, "Authentication Error")
	@ns.marshal_list_with(wallpaper_model)
	def get(self):
		wallpapers: list[dict] = get_wallpapers()
		return wallpapers, 200
		
		
@ns.route("/<int:id>")
class WallpaperRes(Resource):
	@admin_required
	@ns.response(204, "")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "Invalid or missing ID")
	def delete(self, id: int):
		remove_wallpaper(id)
		return "", 204

	@admin_required
	@ns.response(204, "")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "Invalid or missing ID")
	@ns.response(500, "")
	@ns.expect(wallpaper_update_model)
	def patch(self, id: int):
		data: dict = ns.payload
		update_wallpaper(id, data)
		return "", 204
