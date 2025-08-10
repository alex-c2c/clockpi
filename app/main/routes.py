import time
from logging import Logger, getLogger

from flask import request
from flask_restx import Resource

from app import epd, queue, redis_controller, sleep
from app.auth.logic import local_apikey_required, login_required
from app.consts import *
from app.epd.consts import *
from app.epd.logic import *
from app.sleep.logic import *
from app.wallpaper.models import WallpaperModel

from . import ns

logger: Logger = getLogger(__name__)

"""
API
"""

@ns.route("/time")
class TimeRes(Resource):
    @login_required
    def get(self):
        return {"time": time.time()}, 200


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
