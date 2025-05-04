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
	job_ids: list[str]

	def __init__(
		self,
		id: int,
		days: tuple[bool, bool, bool, bool, bool, bool, bool],
		hour: int,
		minute: int,
		duration: int,
	) -> None:
		logger.debug(f"New sleep_schedule: {days=} {hour=} {minute=} {duration=}")

		self.id = id
		self.days = days
		self.hour = hour
		self.minute = minute
		self.duration = duration
		self.job_ids = []
		self.add_job_schedules()

	def update(
		self,
		days: tuple[bool, bool, bool, bool, bool, bool, bool] | None = None,
		hour: int | None = None,
		minute: int | None = None,
		duration: int | None = None,
	) -> None:
		logger.debug(f"sleep_schedule:update {days=} {hour=} {minute=} {duration=}")
		if days is not None:
			self.days = days

		if hour is not None:
			self.hour = hour

		if minute is not None:
			self.minute = minute

		if duration is not None:
			self.duration = duration

		self.remove_job_schedules()
		self.add_job_schedules()

	def remove_job_schedules(self) -> None:
		logger.debug(f"sleep_schedule:remove_job_schedules")
		for id in self.job_ids:
			job_scheduler.remove_cron_job(id)

		self.job_ids.clear()

	def add_job_schedules(self) -> None:
		logger.debug(
			f"sleep_schedule:add_job_schedules {self.id=} {self.days=} {self.hour=} {self.minute=} {self.duration=}"
		)

		if self.duration <= 0 or True not in self.days:
			return

		for day in range(len(self.days)):
			if not self.days[day]:
				continue

			job_active_id: str = f"job_set_sleep_active_{self.id}_{day}"
			job_inactive_id: str = f"job_set_sleep_inactive_{self.id}_{day}"

			# add cron job to sleep display
			job_scheduler.add_cron_job(
				job_active_id, set_active, day, self.hour, self.minute
			)

			# calculate day_of_week compensation if duration crosses over to next day(s)
			duration_hour: int = floor(self.duration / 60)
			duration_minute: int = self.duration % 60

			minute: int = self.minute + duration_minute
			if minute > 59:
				minute %= 60
				duration_hour += 1

			day_end: int = day
			hour: int = self.hour + duration_hour
			if hour > 23:
				day_end += floor(hour / 24)
				day_end %= 7
				hour %= 24

			# Add cron job to wake display
			job_scheduler.add_cron_job(
				job_inactive_id, set_inactive, day_end, hour, minute
			)

			self.job_ids.append(job_active_id)
			self.job_ids.append(job_inactive_id)


bp = Blueprint("sleep", __name__, url_prefix="/sleep")
logger: Logger = getLogger(__name__)
schedules: list[sleep_schedule] = []


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


def init(app: Flask) -> None:
	logger.info(f"Initializing sleep_schedules")

	with app.app_context():
		# Clear existing list
		global schedules
		schedules.clear()

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

			sch: sleep_schedule = sleep_schedule(id, days, hour, minute, duration)
			schedules.append(sch)


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

	# Add to list
	global schedules
	sch: sleep_schedule = sleep_schedule(id, days, hour, minute, duration)
	schedules.append(sch)


def _remove(id: int) -> None:
	logger.info(f"Remove {id=}")

	# Remove from DB
	db.remove_sleep_schedule(id)

	# Remove from list
	global schedules
	for sch in schedules:
		if sch.id == id:
			sch.remove_job_schedules()
			schedules.remove(sch)
			return


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

	# Update list
	global schedules
	for sch in schedules:
		if sch.id == id:
			sch.update(days, hour, minute, duration)
			break

	return True


def set_active() -> None:
	logger.debug(f"set_sleep_active")
	redis_controller.rset(R_SLEEP_ACTIVE, "1")


def set_inactive() -> None:
	logger.debug(f"set_sleep_inactive")
	redis_controller.rset(R_SLEEP_ACTIVE, "0")


def is_active_now() -> bool:
	is_active: bool = (
		True if redis_controller.rget(R_SLEEP_ACTIVE, "0") == "1" else False
	)
	logger.debug(f"is_active_now: {is_active=}")
	return is_active


@bp.route("/")
def index():
	global schedules

	jobs = job_scheduler.get_cron_jobs()
	for j in jobs:
		logger.info(f"{j.id}")

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
