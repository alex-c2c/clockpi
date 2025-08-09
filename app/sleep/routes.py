import time

from flask import request
from flask_restx import Resource
from logging import Logger, getLogger

from app import api
from app.auth.logic import login_required
from app.consts import *

from . import ns
from .logic import SleepSchedule, add, get_schedules, get_status, remove, update

logger: Logger = getLogger(__name__)

"""
API
"""


@ns.route("/")
class SleepListRes(Resource):
	@login_required
	def get(self):
		schedules: list[SleepSchedule] = get_schedules()
		return [sch.to_dict() for sch in schedules], 200


@ns.route("/status")
class SleepStatusRes(Resource):
	@login_required
	def get(self):
		is_sleep: bool = True if get_status() == SLEEP_STATUS_SLEEP else False
		
		return {"isSleep": is_sleep}, 200


@ns.route("/create")
class SleepCreateRes(Resource):
	@login_required
	def post(self):
		d: dict = request.get_json()
		logger.info(f"{d=}")

		start_time: str | None = d.get("startTime")
		duration: int | None = d.get("duration")
		days: tuple[str] | None = d.get("days")
  
		if start_time is None or duration is None or days is None:
			api.abort(400, "Invalid or missing data")
			return
   
		res: int = add(start_time, duration, days)
		if res != 0:
			api.abort(400, "Invalid or missing data")
			return
   
		return {}, 200


@ns.route("/<int:id>")
@api.doc(responses={404: "Invalid or missing ID"}, params={"id": "Schedule ID"})
class SleepRes(Resource):
	@login_required
	def delete(self, id: int):
		result: int = remove(id)
		if result == ERR_SLEEP_INVALID_ID:
			api.abort(404, "Invalid or missing ID")
		return "", 204

	@login_required
	def patch(self, id: int):
		d: dict = request.get_json()
		logger.info(f"{d=}")

		start_time: str | None = d.get("startTime")
		duration: int | None = d.get("duration")
		days: tuple[str] | None = d.get("days")
		enabled: bool | None = d.get("isEnabled")
  
		res: int = update(id, start_time, duration, days, enabled)
  
		if res == 0:
			return "", 204

		elif res == ERR_SLEEP_INVALID_ID:
			api.abort(404, "Invalid or missing ID")

		elif res == ERR_SLEEP_INVALID_DATA:
			api.abort(400, "Invalid data")

		else:
			api.abort(400, "Bad request")
