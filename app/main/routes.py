import time
from logging import Logger, getLogger

from flask import request
from flask_restx import Resource

from app import redis_controller
from app.auth.logic import local_apikey_required
from app.consts import SLEEP_STATUS_AWAKE, SLEEP_STATUS_SLEEP, R_SETTINGS_DRAW_GRIDS
from app.epd.logic import clear_clock_display, update_clock_display
from app.schedule.logic import should_sleep_now, get_status, set_status
from app.queue.logic import shuffle_queue, shift_next

from . import ns

logger: Logger = getLogger(__name__)


"""
API
"""


@ns.route("/tick")
class TickRes(Resource):
	@local_apikey_required
	def get(self):
		sleep_status: int = get_status()
		is_sleep: bool = should_sleep_now()

		if is_sleep:
			if sleep_status == SLEEP_STATUS_AWAKE:
				clear_clock_display()
				set_status(SLEEP_STATUS_SLEEP)
		else:
			update_clock_display()
			if sleep_status == SLEEP_STATUS_SLEEP:
				set_status(SLEEP_STATUS_AWAKE)

		return "", 204


@ns.route("/queue/shuffle")
class QueueShuffleRes(Resource):
	@local_apikey_required
	@ns.response(204, "")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(500, "Internal Server Error")
	def get(self):
		shuffle_queue()
		return "", 204
		

@ns.route("/queue/next")
class QueueNextRes(Resource):
	@local_apikey_required
	@ns.response(204, "")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(500, "Internal Server Error")
	def get(self):
		shift_next()
		return "", 204


@ns.route("/draw_grids")
class DrawGridsRes(Resource):
	@local_apikey_required
	def patch(self):
		d: dict = request.get_json()
		draw_grids: bool | None = d.get("draw_grids")
		if draw_grids is None:
			return {"error": "Missing argument"}, 400

		logger.info(f"set draw grids {draw_grids=}")

		# Update Redis
		redis_controller.rset(R_SETTINGS_DRAW_GRIDS, "1" if draw_grids else "0")

		return "", 204
