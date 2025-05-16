import queue

from app import redis_controller
from logging import Logger, getLogger
from flask import (
	Blueprint,
	redirect,
	render_template,
	request,
	url_for,
)
from app.auth.logic import login_required
from app.consts import *

from app import epd, queue
from app.models import WallpaperModel


bp: Blueprint = Blueprint("main", __name__)
logger: Logger = getLogger(__name__)


@bp.route("/", methods=["GET"])
@login_required
def index():
	return redirect(location=url_for("main.test"))
	# return render_template(("clock/index.html"))


@bp.route("/test", methods=["GET"])
@login_required
def test():
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
def set_draw_grids():
	if request.method == "POST":
		draw_grids: bool = request.form.get("draw_grids", "") == "true"

		logger.info(f"set draw grids {draw_grids=}")

		# Update Redis
		redis_controller.rset(R_SETTINGS_DRAW_GRIDS, "1" if draw_grids else "0")

	return redirect(url_for(endpoint="main.test"))
