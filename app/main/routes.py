import time

from flask_restx import Namespace, Resource
from app import api_v1, epd, queue, redis_controller, sleep
from flask import (
	Blueprint,
	redirect,
	render_template,
	request,
	url_for,
)

from app.auth.logic import apikey_required, login_required
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


"""
Blueprints
"""


@bp.route("/", methods=["GET"])
@login_required
def view_index():
	return redirect(location=url_for("main.view_test"))
	# return render_template(("clock/index.html"))


@bp.route("/test", methods=["GET"])
@login_required
def view_test():
	# Get settings from Redis
	draw_grids: bool = redis_controller.get_draw_grids()
	epd_busy: bool = epd.logic.get_busy()

	# Get all wallpapers
	wallpapers: list = WallpaperModel.query.order_by(WallpaperModel.id).all()

	# Get wallpaper queue
	wallpaper_queue: list[int] = queue.logic.get_queue()

	# Text Color
	text_color: dict[str, int] = {
		"black": COLOR_EPD_BLACK,
		"white": COLOR_EPD_WHITE,
		"yellow": COLOR_EPD_YELLOW,
		"red": COLOR_EPD_RED,
		"blue": COLOR_EPD_BLUE,
		"green": COLOR_EPD_GREEN,
	}
 
	# Time Modes
	mode: dict[str, int] = {
		"off": TIMEMODE_OFF,
		"sect_9_top_left": TIMEMODE_SECT_9_TOP_LEFT,
		"sect_9_top_center": TIMEMODE_SECT_9_TOP_CENTER,
		"sect_9_top_right": TIMEMODE_SECT_9_TOP_RIGHT,
		"sect_9_middle_left": TIMEMODE_SECT_9_MIDDLE_LEFT,
		"sect_9_middle_center": TIMEMODE_SECT_9_MIDDLE_CENTER,
		"sect_9_middle_right": TIMEMODE_SECT_9_MIDDLE_RIGHT,
		"sect_9_bottom_left": TIMEMODE_SECT_9_BOTTOM_LEFT,
		"sect_9_bottom_center": TIMEMODE_SECT_9_BOTTOM_CENTER,
		"sect_9_bottom_right": TIMEMODE_SECT_9_BOTTOM_RIGHT,
		"sect_6_top_left": TIMEMODE_SECT_6_TOP_LEFT,
		"sect_6_top_right": TIMEMODE_SECT_6_TOP_RIGHT,
		"sect_6_middle_left": TIMEMODE_SECT_6_MIDDLE_LEFT,
		"sect_6_middle_right": TIMEMODE_SECT_6_MIDDLE_RIGHT,
		"sect_6_bottom_left": TIMEMODE_SECT_6_BOTTOM_LEFT,
		"sect_6_bottom_right": TIMEMODE_SECT_6_BOTTOM_RIGHT,
		"sect_4_top_left": TIMEMODE_SECT_4_TOP_LEFT,
		"sect_4_top_right": TIMEMODE_SECT_4_TOP_RIGHT,
		"sect_4_bottom_left": TIMEMODE_SECT_4_BOTTOM_LEFT,
		"sect_4_bottom_right": TIMEMODE_SECT_4_BOTTOM_RIGHT,
		"full_1": TIMEMODE_FULL_1,
		"full_2": TIMEMODE_FULL_2,
		"full_3": TIMEMODE_FULL_3,
	}

	return render_template(
		"main/test.html",
		draw_grids=draw_grids,
		epd_busy=epd_busy,
		wallpapers=wallpapers,
		wallpaper_queue=wallpaper_queue,
		text_color=text_color,
		mode=mode,
	)


@bp.route("/draw_grids", methods=["POST"])
@login_required
def view_set_draw_grids():
	if request.method == "POST":
		draw_grids: bool = request.form.get("draw_grids", "") == "true"

		logger.info(f"set draw grids {draw_grids=}")

		# Update Redis
		redis_controller.rset(R_SETTINGS_DRAW_GRIDS, "1" if draw_grids else "0")

	return redirect(url_for(endpoint="main.view_test"))


@bp.route("/time", methods=["GET"])
def get_current_time():
    return {"time": time.time()}
