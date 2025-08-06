import time

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_restx import Namespace, Resource

from app import api_v1
from app.auth.logic import login_required, react_login_required
from app.consts import *
from . import logger
from .logic import SleepSchedule, add, get_schedules, get_status, remove, update


bp = Blueprint("sleep", __name__, url_prefix="/sleep")
ns: Namespace = api_v1.namespace("sleep", description="Sleep operations")


"""
API
"""


@ns.route("/")
class SleepListRes(Resource):
	@react_login_required
	def get(self) -> dict:
		schedules: list[SleepSchedule] = get_schedules()
		return [sch.to_dict() for sch in schedules], 200


@ns.route("/status")
class SleepListRes(Resource):
	@react_login_required
	def get(self) -> dict:
		is_sleep: bool = True if get_status() == SLEEP_STATUS_SLEEP else False
		
		return {"isSleep": is_sleep}, 200


@ns.route("/create")
class SleepCreateRes(Resource):
	@react_login_required
	def post(self) -> dict:
		d: dict = request.get_json()
		logger.info(f"{d=}")

		start_time: str | None = d.get("startTime")
		duration: int | None = d.get("duration")
		days: tuple[str] | None = d.get("days")
  
		if start_time is None or duration is None or days is None:
			api_v1.abort(400, "Invalid or missing data")
   
		res: int = add(start_time, duration, days)
		if res != 0:
			api_v1.abort(400, "Invalid or missing data")
   
		return {}, 200


@ns.route("/<int:id>")
@api_v1.doc(responses={404: "Invalid or missing ID"}, params={"id": "Schedule ID"})
class SleepRes(Resource):
	@react_login_required
	def delete(self, id: int):
		result: int = remove(id)
		if result == ERR_SLEEP_INVALID_ID:
			api_v1.abort(404, "Invalid or missing ID")
		return "", 204

	@react_login_required
	def patch(self, id: int):
		d: dict = request.get_json()
		logger.info(f"{d=}")

		id: int | None = d.get("id")
		start_time: str | None = d.get("startTime")
		duration: int | None = d.get("duration")
		days: tuple[str] | None = d.get("days")
		enabled: bool = d.get("isEnabled")
  
		res: int = update(id, start_time, duration, days, enabled)
  
		if res == 0:
			return "", 204

		elif res == ERR_SLEEP_INVALID_ID:
			api_v1.abort(404, "Invalid or missing ID")

		elif res == ERR_SLEEP_INVALID_DATA:
			api_v1.abort(400, "Invalid data")

		else:
			api_v1.abort(400, "Bad request")
