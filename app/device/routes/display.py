from logging import Logger, getLogger

from flask import session
from flask_restx import Resource

from app.lib.decorators import login_required

from .. import ns
from ..logic.display import clear_display, update_display


logger: Logger = getLogger(__name__)


@ns.route("/<int:device_id>/display/clear")
@ns.param("device_id", "Device ID")
class DeviceDisplayClearRes(Resource):
	@login_required
	@ns.response(204, "Success")
	def post(self, device_id: int):
		user_id: int = session.get("id", 0)
		
		clear_display(user_id, device_id)
		
		return "", 204


@ns.route("/<int:device_id>/display/refresh")
@ns.param("device_id", "Device ID")
class DeviceDisplayRefreshRes(Resource):
	@login_required
	@ns.response(204, "Success")
	def post(self, device_id: int):
		user_id: int = session.get("id", 0)
		
		update_display(user_id, device_id)
		
		return "", 204
