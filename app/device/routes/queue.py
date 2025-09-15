from logging import Logger, getLogger

from flask import session
from flask_restx import Resource

from app.lib.decorators import login_required

from .. import ns
from ..fields import *
from ..fields.queue import *
from ..logic.queue import move_to_first, shift_next, shuffle_queue


logger: Logger = getLogger(__name__)


@ns.route("/<int:device_id>/queue/shuffle")
class DeviceQueueShuffleRes(Resource):
	@login_required
	@ns.response(204, "Success")
	def post(self, device_id: int):
		user_id: int = session.get("id", 0)

		shuffle_queue(user_id, device_id)
		
		return "", 204


@ns.route("/<int:device_id>/queue/next")
class DeviceQueueNextRes(Resource):
	@login_required
	@ns.response(204, "Success")
	def post(self, device_id: int):
		user_id: int = session.get("id", 0)
		
		shift_next(user_id, device_id)
		
		return "", 204


@ns.route("/<int:device_id>/queue/select")
class DeviceQueueSelectRes(Resource):
	@login_required
	@ns.response(204, "Success")
	@ns.expect(queue_select_fields, validate=True)
	def post(self, device_id: int):
		user_id: int = session.get("id", 0)
		payload: dict = ns.payload
		
		move_to_first(user_id, device_id, payload.get("wallpaperId", 0))
		
		return "", 204
