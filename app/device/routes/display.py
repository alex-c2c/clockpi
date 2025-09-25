from logging import Logger, getLogger

from flask import session
from flask_restx import Resource

from app.device.logic import can_access_device
from app.lib.decorators import login_required
from app.lib.errors import ErrorCode, api_abort

from .. import ns
from ..logic.display import clear_display, update_display


logger: Logger = getLogger(__name__)


@ns.route("/<int:device_id>/display/clear")
@ns.param("device_id", "Device ID")
class DeviceDisplayClearRes(Resource):
	@login_required
	@ns.response(204, "Success")
	def post(self, device_id: int):
		user_id: int = session.get("userId", 0)
		
		if not can_access_device(user_id, device_id):
			api_abort(ErrorCode.FORBIDDEN)
		
		clear_display(device_id)
		
		return "", 204


@ns.route("/<int:device_id>/display/refresh")
@ns.param("device_id", "Device ID")
class DeviceDisplayRefreshRes(Resource):
	@login_required
	@ns.response(204, "Success")
	def post(self, device_id: int):
		user_id: int = session.get("userId", 0)
		
		if not can_access_device(user_id, device_id):
			api_abort(ErrorCode.FORBIDDEN)
		
		update_display(device_id)
		
		return "", 204


# NOTE: for debugging purposes
@ns.route("/<int:device_id>/display/test/save")
@ns.param("device_id", "Device ID")
class DeviceDisplaySaveRes(Resource):
	@login_required
	@ns.response(204, "Success")
	def post(self, device_id: int):
		user_id: int = session.get("userId", 0)
		
		if not can_access_device(user_id, device_id):
			api_abort(ErrorCode.FORBIDDEN)
		
		update_display(device_id, True)
		
		return "", 204
