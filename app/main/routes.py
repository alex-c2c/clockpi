from flask_restx import Namespace, Resource
from app import redis_controller, sleep
from flask import (
	Blueprint,
	redirect,
	render_template,
	request,
	url_for,
)

from app import api_v1, epd, queue
from app.auth.logic import apikey_required, login_required
from app.consts import *
from . import logger
from app.models import WallpaperModel


bp: Blueprint = Blueprint("main", __name__)
ns: Namespace = api_v1.namespace("main", description="Main operations")


"""
API
"""


@ns.route("/tick")
class TickRes(Resource):
	@apikey_required
	def get(self) -> dict:
		sleep_status: SleepStatus = sleep.logic.get_status()
		should_sleep_now: bool = sleep.logic.should_sleep_now()
		logger.debug(f"job_update_clock {sleep_status=} {should_sleep_now=}")

		if should_sleep_now:
			if sleep_status == SleepStatus.AWAKE:
				epd.logic.clear_display()
				sleep.logic.set_status(SleepStatus.SLEEP)
		else:
			epd.logic.update_display()
			if sleep_status == SleepStatus.SLEEP:
				sleep.logic.set_status(SleepStatus.AWAKE)

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
	text_color: dict[str, int] = TEXT_COLOR_DICT

	# Time Modes
	mode: dict[str, int] = TIME_MODE_DICT

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
