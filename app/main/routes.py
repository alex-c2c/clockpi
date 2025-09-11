from logging import Logger, getLogger

from flask import request
from flask_restx import Resource

from app.consts import SleepStatus
from app.device.logic.display import clear_display, update_display
from app.device.logic.queue import shift_next, shuffle_queue
from app.lib.decorators import local_apikey_required
from app.schedule.logic import get_status, set_status, should_sleep_now

from . import ns

logger: Logger = getLogger(__name__)


"""
API
"""


@ns.route("/<int:device_id>/tick")
class TickRes(Resource):
	@local_apikey_required
	def get(self, device_id: int):
		sleep_status: SleepStatus = get_status(0, device_id, True)
		is_sleep: bool = should_sleep_now(0, device_id, True)

		if is_sleep:
			if sleep_status == SleepStatus.AWAKE:
				clear_display(0, device_id, True)
				set_status(0, device_id, SleepStatus.SLEEP, True)
		else:
			update_display(0, device_id, True)
			if sleep_status == SleepStatus.SLEEP:
				set_status(0, device_id, SleepStatus.SLEEP, True)
				
		return "", 204


@ns.route("/<int:device_id>/queue/shuffle")
class QueueShuffleRes(Resource):
	@local_apikey_required
	@ns.response(204, "")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(500, "Internal Server Error")
	def get(self, device_id: int):
		
		shuffle_queue(0, device_id, True)
		
		return "", 204
		

@ns.route("/<int:device_id>/queue/next")
class QueueNextRes(Resource):
	@local_apikey_required
	@ns.response(204, "")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(500, "Internal Server Error")
	def get(self, device_id: int):
		
		shift_next(0, device_id, True)
		
		return "", 204
