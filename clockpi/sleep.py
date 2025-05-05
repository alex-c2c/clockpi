from logging import Logger, getLogger
from math import floor
from typing import Any
from flask import (
	Blueprint,
	Flask,
	flash,
	redirect,
	render_template,
	request,
	url_for,
)

from clockpi.auth import login_required
from clockpi.consts import *
from clockpi import db, job_scheduler, redis_controller


class sleep_schedule:
	id: int
	days: tuple[bool, bool, bool, bool, bool, bool, bool]
	hour: int
	minute: int
	duration: int

	def __init__(
		self,
		id: int,
		days: tuple[bool, bool, bool, bool, bool, bool, bool],
		hour: int,
		minute: int,
		duration: int,
	) -> None:
		self.id = id
		self.days = days
		self.hour = hour
		self.minute = minute
		self.duration = duration


bp = Blueprint("sleep", __name__, url_prefix="/sleep")
logger: Logger = getLogger(__name__)


"""
hour: between 0 and 23 (inclusive)
minute: between 0 and 59 (inclusive)
duration: >= 0, if 0, do not add cron job
"""


def _validate(hour: int, minute: int, duration: int) -> int:
	invalid: bool = False

	if hour < 0 or hour > 23:
		logger.error(f"Invalid hour, {hour=}")
		invalid = True

	if minute < 0 or minute > 59:
		logger.error(f"Invalid minute, {minute=}")
		invalid = True

	if duration < 0:
		logger.error(f"Invalid duration, {duration=}")
		invalid = True

	if invalid:
		return ERR_SCH_INVALID_DATA

	return 0


def _remove_job_schedules(id: int) -> None:
	logger.debug(f"remove_job_schedules {id=}")

	job_ids: list[str] = job_scheduler.get_cron_jobs()
	for job_id in job_ids:
		if f"job_set_sleep_{id}" in job_id or f"job_set_awake_{id}" in job_id:
			job_scheduler.remove_cron_job(job_id)


def _add_job_schedules(
	id: int,
	days: tuple[bool, bool, bool, bool, bool, bool, bool],
	hour: int,
	minute: int,
	duration: int,
) -> None:
	logger.debug(f"add_job_schedules {id=} {days=} {hour=} {minute=} {duration=}")

	if duration <= 0 or True not in days:
		return

	for day in range(len(days)):
		if not days[day]:
			continue

		job_sleep_id: str = f"job_set_sleep_{id}_{day}"
		job_awake_id: str = f"job_set_awake_{id}_{day}"

		# add cron job to sleep display
		job_scheduler.add_cron_job(job_sleep_id, set_sleep, day, hour, minute)

		# calculate day_of_week compensation if duration crosses over to next day(s)
		duration_hour: int = floor(duration / 60)
		duration_minute: int = duration % 60

		minute += duration_minute
		if minute > 59:
			minute %= 60
			duration_hour += 1

		day_end: int = day
		hour += duration_hour
		if hour > 23:
			day_end += floor(hour / 24)
			day_end %= 7
			hour %= 24

		# Add cron job to wake display
		job_scheduler.add_cron_job(job_awake_id, set_awake, day_end, hour, minute)


def init(app: Flask) -> None:
	logger.info(f"Initializing sleep_schedules")

	with app.app_context():
		# Get from DB and check if empty
		data: list[Any] = db.get_sleep_schedules()
		if data is None or len(data) == 0:
			logger.debug(f"No sleep schedules")
			return

		# Initializing list
		for sch in data:
			days: tuple[bool, bool, bool, bool, bool, bool, bool] = tuple(
				True if day == "1" else False for day in sch["days"].split("^")
			)
			id: int = sch["id"]
			hour: int = sch["hour"]
			minute: int = sch["minute"]
			duration: int = sch["duration"]

			_add_job_schedules(id, days, hour, minute, duration)
   
		redis_controller.rset(R_SLEEP_STATUS, str(SleepStatus.AWAKE.value))


def _add(
	days: tuple[bool, bool, bool, bool, bool, bool, bool],
	hour: int,
	minute: int,
	duration: int,
) -> int:
	logger.info(f"Add {days=} {hour=} {minute=} {duration=}")

	# validate inputs
	result: int = _validate(hour, minute, duration)
	if result != 0:
		return result

	# Add to DB
	id: int = db.add_sleep_schedule(days, hour, minute, duration)

	# add new job schedules
	_add_job_schedules(id, days, hour, minute, duration)


def _remove(id: int) -> None:
	logger.info(f"Remove {id=}")

	# Remove from DB
	db.remove_sleep_schedule(id)

	# remove job schedules
	_remove_job_schedules(id)


def _update(
	id: int,
	days: tuple[bool, bool, bool, bool, bool, bool, bool],
	hour: int,
	minute: int,
	duration: int,
) -> bool:
	logger.info(f"Update {id=} {days=} {hour=} {minute=} {duration=}")

	# Validate inputs
	result: int = _validate(hour, minute, duration)
	if result != 0:
		return result

	# Update DB
	db.update_sleep_schedule(id, days, hour, minute, duration)

	# update job schedules
	_remove_job_schedules(id)
	_add_job_schedules(id, days, hour, minute, duration)

	return True


def set_awake() -> None:
	logger.debug(f"set_sleep_active")
	redis_controller.rset(R_SLEEP_STATUS, str(SleepStatus.PENDING_AWAKE.value))


def set_sleep() -> None:
	logger.debug(f"set_sleep_inactive")
	redis_controller.rset(R_SLEEP_STATUS, str(SleepStatus.PENDING_SLEEP.value))


@bp.route("/")
def index():
	schedules: list[sleep_schedule] = []
	data: list[Any] = db.get_sleep_schedules()

	# Initializing list
	for sch in data:
		days: tuple[bool, bool, bool, bool, bool, bool, bool] = tuple(
			True if day == "1" else False for day in sch["days"].split("^")
		)
		id: int = sch["id"]
		hour: int = sch["hour"]
		minute: int = sch["minute"]
		duration: int = sch["duration"]

		sch: sleep_schedule = sleep_schedule(id, days, hour, minute, duration)
		schedules.append(sch)

	return render_template(
		("sleep/index.html"),
		schedules=schedules,
	)


@bp.route("/add", methods=["GET"])
@login_required
def add():
	if request.method != "GET":
		flash(f"Invalid method")
		return redirect(location=url_for("sleep.index"))

	_add((False, False, False, False, False, False, False), 0, 0, 0)

	return redirect(location=url_for("sleep.index"))


@bp.route("/remove/<int:id>", methods=["GET"])
@login_required
def remove(id: int):
	if request.method != "GET":
		flash(f"Invalid method")
		return redirect(location=url_for("sleep.index"))

	_remove(id)

	return redirect(location=url_for("sleep.index"))


@bp.route("/update/<int:id>", methods=["POST"])
@login_required
def update(id: int):
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
		return redirect(location=url_for(endpoint="sleep.index"))

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

	_update(id, days, hour, minute, duration)

	return redirect(location=url_for(endpoint="sleep.index"))
