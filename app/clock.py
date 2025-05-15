import queue
import os

from app import epd, redis_controller, queue, wallpaper
from datetime import datetime
from logging import Logger, getLogger
from threading import Thread
from flask import (
	Blueprint,
	current_app,
	flash,
	redirect,
	render_template,
	request,
	url_for,
)
from app.auth import login_required
from app.consts import *

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from app.models import WallpaperModel


bp: Blueprint = Blueprint("clock", __name__)
logger: Logger = getLogger(__name__)


def allowed_file(filename) -> bool:
	return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/", methods=["GET"])
@login_required
def index():
	return redirect(location=url_for("clock.test"))
	#return render_template(("clock/index.html"))


@bp.route("/test", methods=["GET"])
@login_required
def test():
	# Get settings from Redis
	draw_grids: bool = redis_controller.get_draw_grids()
	epd_busy: bool = epd.get_busy()

	# Get all wallpapers
	wallpapers: list = WallpaperModel.query.order_by(WallpaperModel.id).all()

	# Get wallpaper queue
	wallpaper_queue: list[int] = queue.get_queue()

	# Text Color
	text_color: dict[str, int] = TEXT_COLOR_DICT

	# Time Modes
	mode: dict[str, int] = TIME_MODE_DICT

	# Sleep Schedules
	now_hr: int = datetime.now().hour
	now_min: int = datetime.now().minute

	return render_template(
		"clock/test.html",
		draw_grids=draw_grids,
		epd_busy=epd_busy,
		wallpapers=wallpapers,
		wallpaper_queue=wallpaper_queue,
		text_color=text_color,
		mode=mode,
	)


@bp.route("/clock/clear", methods=["GET"])
@login_required
def clear():
	epd.clear()

	return redirect(location=url_for("clock.test"))


@bp.route("/clock/refresh", methods=["GET"])
@login_required
def refresh():
	epd.update()

	return redirect(location=url_for("clock.test"))


@bp.route("/clock/draw_grids", methods=["POST"])
@login_required
def set_draw_grids():
	if request.method == "POST":
		draw_grids: bool = request.form.get("draw_grids", "") == "true"

		logger.info(f"set draw grids {draw_grids=}")

		# Update Redis
		redis_controller.rset(R_SETTINGS_DRAW_GRIDS, "1" if draw_grids else "0")

	return redirect(url_for(endpoint="clock.test"))
