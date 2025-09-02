import os
from logging import Logger, getLogger
from threading import Thread

from flask import current_app, request, send_from_directory
from flask_restx import Resource, reqparse
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from app.consts import *
from app.epd.consts import *
from app.lib.decorators import admin_required, local_apikey_required, login_required
from app.queue.logic import get_first_in_queue

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


@ns.route("/upload-test")
class UploadTestRes(Resource):
	@admin_required
	def post(self):
		if "file" not in request.files:
			return
		
		files: list[FileStorage] = request.files.getlist("file")
		
		#logger.debug(request.form)
		logger.debug(request.form.get("offsetX"))
		logger.debug(request.form.get("offsetY"))
		logger.debug(request.form.get("scale"))
		
		scale_str: str | None = request.form.get("scale")
		offset_x_str: str | None = request.form.get(key="offsetX")
		offset_y_str: str | None = request.form.get(key="offsetY")

		if scale_str is None:
			ns.abort(400, "Invalid scale")
			return
		
		if offset_x_str is None:
			ns.abort(400, "Invalid offsetX")
			return
		
		if offset_y_str is None:
			ns.abort(400, "Invalid offsetY")
			return
		
		try:
			scale: float = float(scale_str)
		except ValueError as e:
			ns.abort(400, "Invalid scale")
			return
			
		try:
			offset_x: int = int(offset_x_str)
		except ValueError as e:
			ns.abort(400, "Invalid offsetX")
			return
		
		try:
			offset_y: int = int(offset_y_str)
		except ValueError as e:
			ns.abort(400, "Invalid offsetY")
			return
			
		
		return "", 204


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
			ns.abort(400, "Missing file")
			return

		files: list[FileStorage] = request.files.getlist("file")
		if len(files) == 0:
			ns.abort(400, "Missing file")
			return
		
		file: FileStorage = files[0]

		# Validate file first
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
		
		# retrieve additional parameters required to scale / crop the uploaded file
		scale_str: str | None = request.form.get("scale")
		x_per_str: str | None = request.form.get(key="xPercent")
		y_per_str: str | None = request.form.get(key="yPercent")
		
		logger.debug(f"Upload: {scale_str=} {x_per_str=} {y_per_str=}")
		
		if scale_str is None:
			ns.abort(400, "Invalid scale")
			return
		
		if x_per_str is None:
			ns.abort(400, "Invalid xPercent")
			return
		
		if y_per_str is None:
			ns.abort(400, "Invalid yPercent")
			return
		
		try:
			scale: float = float(scale_str)
		except ValueError as e:
			ns.abort(400, "Invalid scale")
			return
			
		try:
			x_per: float = float(x_per_str)
		except ValueError as e:
			ns.abort(400, "Invalid offsetX")
			return
		
		try:
			y_per: float = float(y_per_str)
		except ValueError as e:
			ns.abort(400, "Invalid offsetY")
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
				scale,
				x_per,
				y_per
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
