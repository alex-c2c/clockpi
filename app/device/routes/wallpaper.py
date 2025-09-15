from logging import Logger, getLogger

from flask import session, request, send_from_directory
from flask_restx import Resource, reqparse

from app import api
from app.consts import DIR_APP_UPLOAD
from app.lib.decorators import admin_required, login_required, local_apikey_required
from app.wallpaper.logic import create_wallpaper, delete_wallpaper, update_wallpaper, get_wallpapers, get_wallpaper_name

from .. import ns
from ..fields import *
from ..fields.wallpaper import *


logger: Logger = getLogger(__name__)


wallpaper_id_parser = reqparse.RequestParser()
wallpaper_id_parser.add_argument("id", type=int, help="Get by wallpaper ID", required=True)

#wallpaper_list_parser = reqparse.RequestParser()
#wallpaper_list_parser.add_argument("id", type=int, help="Filter by wallpaper ID", required=True, action="append")

upload_parser = api.parser()
upload_parser = upload_parser.add_argument("file", location="files", type="FileStorage", required=True)
upload_parser = upload_parser.add_argument("imgScalePer", type=str, location="form", required=True)
upload_parser = upload_parser.add_argument("xPosPer", type=str, location="form", required=True)
upload_parser = upload_parser.add_argument("yPosPer", type=str, location="form", required=True)


@ns.route("/wallpaper/file")
class FileRes(Resource):
	@local_apikey_required
	@ns.produces(["image/bmp"])
	@ns.response(200, "Success")
	@ns.expect(wallpaper_id_parser)
	def get(self):
		user_id: int = session.get("id", 0)
		wallpaper_id: int | None = wallpaper_id_parser.parse_args().get("id")
		file_name: str = get_wallpaper_name(user_id, wallpaper_id)
		
		return send_from_directory(DIR_APP_UPLOAD, file_name)


@ns.route("/<int:device_id>/wallpapers")
class DeviceWallpaperListRes(Resource):
	@login_required
	@ns.response(200, "Success", wallpaper_fields)
	@ns.marshal_with(wallpaper_fields, as_list=True)
	def get(self, device_id: int):
		user_id: int = session.get("id", 0)
		
		wallpapers: list[dict] = get_wallpapers(user_id, device_id)
		
		return wallpapers, 200


@ns.route("/<int:device_id>/wallpaper/upload")
class DeviceWallpaperUploadRes(Resource):
	@login_required
	@ns.expect(upload_parser, validate=True)
	@ns.response(204, "Success")
	def post(self, device_id: int):
		user_id: int = session.get("id", 0)
		
		logger.info(f"{request.files=}")
		logger.info(f"{request=}")
				
		create_wallpaper(
			user_id,
			device_id,
			request.files.get("file"),
			request.form
		)

		return "", 204


@ns.route("/wallpaper/<int:wallpaper_id>")
class WallpaperRes(Resource):
	@admin_required
	@ns.response(204, "")
	def delete(self, wallpaper_id: int):
		user_id: int = session.get("id", 0)

		delete_wallpaper(user_id, wallpaper_id)

		return "", 204

	@admin_required
	@ns.response(204, "")
	@ns.expect(wallpaper_update_fields)
	def patch(self, wallpaper_id: int):
		user_id: int = session.get("id", 0)
		payload: dict = ns.payload
		
		update_wallpaper(user_id, wallpaper_id, payload)
		
		return "", 204
