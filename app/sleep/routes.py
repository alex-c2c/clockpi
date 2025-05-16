from logging import Logger, getLogger
from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.auth.logic import login_required

from app.sleep import logic
from app.sleep.logic import SleepSchedule


bp = Blueprint("sleep", __name__, url_prefix="/sleep")
logger: Logger = getLogger(__name__)


@bp.route("/")
def view_index():
	schedules: list[SleepSchedule] = logic.get_schedules()

	return render_template(
		("sleep/index.html"),
		schedules=schedules,
	)


@bp.route("/add", methods=["GET"])
@login_required
def view_add():
	if request.method != "GET":
		flash(f"Invalid method")
		return redirect(location=url_for("sleep.view_index"))

	logic.add((False, False, False, False, False, False, False), 0, 0, 0)

	return redirect(location=url_for("sleep.view_index"))


@bp.route("/remove/<int:id>", methods=["GET"])
@login_required
def view_remove(id: int):
	if request.method != "GET":
		flash(f"Invalid method")
		return redirect(location=url_for("sleep.view_index"))

	logic.remove(id)

	return redirect(location=url_for("sleep.view_index"))


@bp.route("/update/<int:id>", methods=["POST"])
@login_required
def view_update(id: int):
	if request.method != "POST":
		flash(f"Invalid method")
		return redirect(location=url_for("sleep.index"))

	mon: bool = True if request.form.get("mon") is not None else False
	tue: bool = True if request.form.get("tue") is not None else False
	wed: bool = True if request.form.get("wed") is not None else False
	thu: bool = True if request.form.get("thu") is not None else False
	fri: bool = True if request.form.get("fri") is not None else False
	sat: bool = True if request.form.get("sat") is not None else False
	sun: bool = True if request.form.get("sun") is not None else False

	invalid_data: bool = False
	if request.form.get("hour") is None:
		flash(f"Missing starting hours")
		invalid_data = True

	if request.form.get("minute") is None:
		flash(f"Missing starting minutes")
		invalid_data = True

	if request.form.get("duration") is None:
		flash(f"Missing duration")
		invalid_data = True

	if invalid_data:
		return redirect(location=url_for(endpoint="sleep.view_index"))

	def tryget(key: str, default: str):
		if request.form.get(key) is None:
			return default

		return request.form.get(key)

	hour: int = int(tryget("hour", "0"))
	minute: int = int(tryget("minute", "0"))
	duration: int = int(tryget("duration", "0"))

	days: tuple[bool, bool, bool, bool, bool, bool, bool] = (
		mon,
		tue,
		wed,
		thu,
		fri,
		sat,
		sun,
	)

	logic.update(id, days, hour, minute, duration)

	return redirect(location=url_for(endpoint="sleep.view_index"))
