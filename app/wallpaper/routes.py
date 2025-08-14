import os
from logging import Logger, getLogger
from threading import Thread

from flask import current_app, request, send_from_directory
from flask_restx import Resource, reqparse
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

parser = reqparse.RequestParser()
parser.add_argument("id", type=int, help="Wallpaper ID (0 == current)", default=0)

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
			return

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


@ns.route("/file")
class FileRes(Resource):
	@local_apikey_required
	@ns.response(200, "")
	@ns.response(400, "Bad Request")
	@ns.response(401, "Authentication Error")
	@ns.response(404, "Wallpaper resource not found")
	@ns.response(404, "Wallpaper image not found")
	@ns.expect(parser)
	def get(self):
		id: int | None = parser.parse_args().get("id")
		
		if id == 0 or id is None:
			id = get_first_in_queue()
		
		file_name: str= get_wallpaper_name(id)
		return send_from_directory(DIR_APP_UPLOAD, file_name)


@ns.route("")
class WallpaperListRes(Resource):
	@login_required
	@ns.response(200, "", wallpaper_model)
	@ns.response(401, "Authentication Error")
	@ns.marshal_with(wallpaper_model, as_list=True)
	def get(self):
		wallpapers: list[dict] = get_wallpapers()
		return wallpapers, 200
		
		
@ns.route("/<int:id>")
class WallpaperRes(Resource):
	@admin_required
	@ns.response(204, "")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "Wallpaper resource not found")
	def delete(self, id: int):
		remove_wallpaper(id)
		return "", 204

	@admin_required
	@ns.response(204, "")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "Wallpaper resource not found")
	@ns.response(500, "")
	@ns.expect(wallpaper_update_model)
	def patch(self, id: int):
		data: dict = ns.payload
		update_wallpaper(id, data)
		return "", 204
