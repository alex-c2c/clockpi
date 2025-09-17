from logging import Logger, getLogger

from flask import session
from flask_restx import Resource

from app.device.logic import can_access_device
from app.lib.decorators import login_required
from app.lib.errors import api_abort, ErrorCode

from .. import ns
from ..fields import *
from ..fields.queue import *
from ..logic.queue import move_to_first, shift_next, shuffle_queue


logger: Logger = getLogger(__name__)


@ns.route("/<int:device_id>/queue/shuffle")
@ns.param("device_id", "Device ID")
class DeviceQueueShuffleRes(Resource):
	@login_required
	@ns.response(204, "Success")
	def post(self, device_id: int):
		user_id: int = session.get("userId", 0)
		
		if not can_access_device(user_id, device_id):
			api_abort(ErrorCode.FORBIDDEN)

		shuffle_queue(device_id)
		
		return "", 204


@ns.route("/<int:device_id>/queue/next")
@ns.param("device_id", "Device ID")
class DeviceQueueNextRes(Resource):
	@login_required
	@ns.response(204, "Success")
	def post(self, device_id: int):
		user_id: int = session.get("userId", 0)
		
		if not can_access_device(user_id, device_id):
			api_abort(ErrorCode.FORBIDDEN)
		
		shift_next(device_id)
		
		return "", 204


@ns.route("/<int:device_id>/queue/select")
class DeviceQueueSelectRes(Resource):
	@login_required
	@ns.response(204, "Success")
	@ns.expect(queue_select_fields, validate=True)
	def post(self, device_id: int):
		user_id: int = session.get("userId", 0)
		payload: dict = ns.payload
		
		if not can_access_device(user_id, device_id):
			api_abort(ErrorCode.FORBIDDEN)
		
		move_to_first(device_id, payload.get("wallpaperId", 0))
		
		return "", 204
