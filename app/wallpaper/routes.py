import os
from logging import Logger, getLogger
from threading import Thread

from flask import current_app, request, send_from_directory, session
from flask_restx import Resource, reqparse
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from app.consts import *
from app.epd7in3e.consts import *
from app.lib.decorators import admin_required, local_apikey_required
from app.lib.errors import api_abort, ErrorCode

from . import ns
from .consts import *
from .fields import *
from .logic import *

logger: Logger = getLogger(__name__)

file_parser = reqparse.RequestParser()
file_parser.add_argument("id", type=int, help="Get by wallpaper ID", required=True)

list_parser = reqparse.RequestParser()
list_parser.add_argument("id", type=int, help="Filter by wallpaper ID", required=True, action="append")


"""
API
"""

@ns.route("/upload")
class UploadRes(Resource):
	@admin_required
	@ns.response(204, "Success")
	@ns.response(400, "Bad Request")
	@ns.response(400, "Invalid file name")
	@ns.response(400, "Invalid file extension")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(413, "Content too large")
	def post(self):
		user_id: int = session.get("id", 0)


		# Check for file in request.files
		files: list[FileStorage] = request.files.getlist("file")
		if len(files) == 0:
			api_abort(ErrorCode.INVALID_INPUT, fields={"file":"This is a required field"})
		
		file: FileStorage = files[0]

		# Validate file first
		file_name: str | None = file.filename
		if file_name is None or len(file_name) == 0:
			api_abort(ErrorCode.INVALID_INPUT, fields={"file":"Invalid input"})
		
		if (
			"." not in file_name
			or file_name.rsplit(".", 1)[1].lower() not in ALLOWED_EXTENSIONS
		):
			api_abort(ErrorCode.UNSUPPORTED_MEDIA_TYPE, detail="Invalid file extension")

		
		# retrieve additional parameters required to scale / crop the uploaded file
		img_scale_per_str: str | None = request.form.get("imgScalePer")
		x_pos_per_str: str | None = request.form.get("xPosPer")
		y_pos_per_str: str | None = request.form.get("yPosPer")
		device_id_str: str | None = request.form.get("deviceId")
		
		logger.debug(f"Upload: {device_id_str=} {img_scale_per_str=} {x_pos_per_str=} {y_pos_per_str=}")
		
		if img_scale_per_str is None:
			api_abort(ErrorCode.INVALID_INPUT, fields={"imgScalePer":"This is a required field"})
		
		if x_pos_per_str is None:
			api_abort(ErrorCode.INVALID_INPUT, fields={"xPosPer":"This is a required field"})
		
		if y_pos_per_str is None:
			api_abort(ErrorCode.INVALID_INPUT, fields={"yPosPer":"This is a required field"})
		
		if device_id_str is None:
			api_abort(ErrorCode.INVALID_INPUT, fields={"deviceId":"This is a required field"})
					
		failed_validations: dict = {}
		
		try:
			img_scale_per: float = float(img_scale_per_str)
		except ValueError as e:
			failed_validations["imgScalePer"] = "Invalid input (float required)"
			
		try:
			x_pos_per: float = float(x_pos_per_str)
		except ValueError as e:
			failed_validations["xPosPer"] = "Invalid input (float required)"
		
		try:
			y_pos_per: float = float(y_pos_per_str)
		except ValueError as e:
			failed_validations["yPosPer"] = "Invalid input (float required)"

		try:
			device_id: int = int(device_id_str)
		except ValueError as e:
			failed_validations["deviceId"] = "Invalid input (integer required)"

		if len(failed_validations.values()) > 0:
			api_abort(ErrorCode.VALIDATION_ERROR, fields= failed_validations)

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
				user_id,
				device_id,
				img_scale_per,
				x_pos_per,
				y_pos_per
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
	@ns.expect(file_parser)
	def get(self):
		user_id: int = session.get("id", 0)
		wallpaper_id: int | None = file_parser.parse_args().get("id")
		file_name: str= get_wallpaper_name(user_id, wallpaper_id)
		
		return send_from_directory(DIR_APP_UPLOAD, file_name)


@ns.route("/<int:wallpaper_id>")
class WallpaperRes(Resource):
	@admin_required
	@ns.response(204, "")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "Wallpaper resource not found")
	def delete(self, wallpaper_id: int):
		user_id: int = session.get("id", 0)

		delete_wallpaper(user_id, wallpaper_id)

		return "", 204

	@admin_required
	@ns.response(204, "")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "Wallpaper resource not found")
	@ns.response(500, "")
	@ns.expect(wallpaper_update_model)
	def patch(self, wallpaper_id: int):
		user_id: int = session.get("id", 0)
		payload: dict = ns.payload
		
		update_wallpaper(user_id, wallpaper_id, payload)
		
		return "", 204
