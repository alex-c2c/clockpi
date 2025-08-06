import time

from flask_restx import Namespace, Resource
from app import api_v1, epd, queue, redis_controller, sleep
from flask import (
	Blueprint,
	redirect,
	render_template,
	request,
	session,
	url_for,
)

from app.auth.logic import apikey_required, login_required, react_login_required
from app.consts import *
from app.epd.consts import *
from app.models import WallpaperModel

from . import logger


bp: Blueprint = Blueprint("main", __name__)
ns: Namespace = api_v1.namespace("main", description="Main operations")


"""
API
"""

@ns.route("/time")
class TimeRes(Resource):
    @react_login_required
    def get(self) -> dict:
        return {"time": time.time()}, 200


@ns.route("/tick")
class TickRes(Resource):
	@apikey_required
	def get(self) -> dict:
		sleep_status: int = sleep.logic.get_status()
		should_sleep_now: bool = sleep.logic.should_sleep_now()
		logger.debug(f"tick {sleep_status=} {should_sleep_now=}")

		if should_sleep_now:
			if sleep_status == SLEEP_STATUS_AWAKE:
				epd.logic.clear_clock_display()
				sleep.logic.set_status(SLEEP_STATUS_SLEEP)
		else:
			epd.logic.update_clock_display()
			if sleep_status == SLEEP_STATUS_SLEEP:
				sleep.logic.set_status(SLEEP_STATUS_AWAKE)

		return "", 204


@ns.route("/test")
class TestRes(Resource):
	@apikey_required
	def get(self) -> dict:
		d: dict = {}

		# Get settings from Redis
		d["draw_grids"] = redis_controller.get_draw_grids()
		d["epd_busy"] = epd.logic.get_busy()

		# Get all wallpapers
		wallpapers: list = WallpaperModel.query.order_by(WallpaperModel.id).all()
		d["wallpapers"] = []
		for wallpaper in wallpapers:
			d["wallpapers"].append(wallpaper.to_dict())

		# Get wallpaper queue
		d["queue"] = queue.logic.get_queue()

		# Text Color
		# text_color: dict[str, int] = TEXT_COLOR_DICT

		# Time Modes
		# mode: dict[str, int] = TIME_MODE_DICT

		return d, 200


@ns.route("/draw_grids")
class DrawGridsRes(Resource):
	@apikey_required
	def patch(self) -> dict:
		d: dict = request.get_json()
		draw_grids: bool | None = d.get("draw_grids")
		if draw_grids is None:
			return {"error": "Missing argument"}, 400

		logger.info(f"set draw grids {draw_grids=}")

		# Update Redis
		redis_controller.rset(R_SETTINGS_DRAW_GRIDS, "1" if draw_grids else "0")

		return "", 204
