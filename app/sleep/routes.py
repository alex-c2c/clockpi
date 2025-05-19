from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_restx import Namespace, Resource

from app import api_v1
from app.auth.logic import apikey_required, login_required
from app.consts import *
from . import logger
from .logic import SleepSchedule, add, get_schedules, remove, update


bp = Blueprint("sleep", __name__, url_prefix="/sleep")
ns: Namespace = api_v1.namespace("sleep", description="Sleep operations")


"""
API
"""


@ns.route("/")
class SleepListRes(Resource):
	@apikey_required
	def get(self) -> dict:
		schedules: list[SleepSchedule] = get_schedules()
		return [sch.to_dict() for sch in schedules], 200

	@apikey_required
	def post(self) -> dict:
		d: dict = request.get_json()
		logger.info(f"{d=}")

		def try_get_bool(day: str) -> bool:
			return (
				d.get(day)
				if d.get(day) is not None and type(d.get(day)) is bool
				else False
			)

		def try_get_int(key: str) -> int:
			return (
				d.get(key) if d.get(key) is not None and type(d.get(key)) is int else 0
			)

		mon: bool = try_get_bool("mon")
		tue: bool = try_get_bool("tue")
		wed: bool = try_get_bool("wed")
		thu: bool = try_get_bool("thu")
		fri: bool = try_get_bool("fri")
		sat: bool = try_get_bool("sat")
		sun: bool = try_get_bool("sun")

		hour: int = try_get_int("hour")
		minute: int = try_get_int("minute")
		duration: int = try_get_int("duration")

		add(mon, tue, wed, thu, fri, sat, sun, hour, minute, duration)

		return "", 204


@ns.route("/<int:id>")
@api_v1.doc(responses={400: "Schedule ID not found"}, params={"id": "Schedule ID"})
class SleepRes(Resource):
	@apikey_required
	def delete(self, id: int):
		result: int = remove(id)
		if result == ERR_SLEEP_INVALID_ID:
			api_v1.abort(400, "Schedule ID not found")
		return "", 204

	@apikey_required
	def patch(self, id: int):
		d: dict = request.get_json()
		logger.info(f"{d=}")

		def try_get_bool(day: str) -> bool | None:
			return (
				d.get(day)
				if d.get(day) is not None and type(d.get(day)) is bool
				else None
			)

		def try_get_int(key: str) -> int | None:
			return (
				d.get(key)
				if d.get(key) is not None and type(d.get(key)) is int
				else None
			)

		mon: bool | None = try_get_bool("mon")
		tue: bool | None = try_get_bool("tue")
		wed: bool | None = try_get_bool("wed")
		thu: bool | None = try_get_bool("thu")
		fri: bool | None = try_get_bool("fri")
		sat: bool | None = try_get_bool("sat")
		sun: bool | None = try_get_bool("sun")

		hour: int | None = try_get_int("hour")
		minute: int | None = try_get_int("minute")
		duration: int | None = try_get_int("duration")

		result: int = update(
			id, mon, tue, wed, thu, fri, sat, sun, hour, minute, duration
		)

		if result == 0:
			return "", 204

		elif result == ERR_SLEEP_INVALID_ID:
			api_v1.abort(400, "Schedule ID not found")

		elif result == ERR_SLEEP_INVALID_DATA:
			api_v1.abort(400, "Invalid data")

		else:
			api_v1.abort(400, "Bad request")


"""
Blueprints
"""


@bp.route("/")
def view_index():
	schedules: list[SleepSchedule] = get_schedules()

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

	add(False, False, False, False, False, False, False, 0, 0, 0)

	return redirect(location=url_for("sleep.view_index"))


@bp.route("/remove/<int:id>", methods=["GET"])
@login_required
def view_remove(id: int):
	if request.method != "GET":
		flash(f"Invalid method")
		return redirect(location=url_for("sleep.view_index"))

	remove(id)

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

	update(id, mon, tue, wed, thu, fri, sat, sun, hour, minute, duration)

	return redirect(location=url_for(endpoint="sleep.view_index"))
