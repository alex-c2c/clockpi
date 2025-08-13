from flask_restx import Resource
from logging import Logger, getLogger

from app.auth.logic import admin_required, login_required
from app.consts import *

from . import ns
from .fields import *
from .logic import *

logger: Logger = getLogger(__name__)


"""
API
"""


@ns.route("")
class ScheduleListRes(Resource):
	@login_required
	@ns.response(200, "List of schedule fields", model=schedule_list_fields)
	@ns.response(401, "Authentication Error")
	@ns.marshal_with(schedule_list_fields)
	def get(self):
		schedules: list[dict] = get_schedules()
		return schedules, 200


@ns.route("/status")
class SleepStatusRes(Resource):
	@login_required
	@ns.response(200, "Is sleeping now", model=sleep_status_fields)
	@ns.response(401, "Authentication Error")
	@ns.response(500, "Internal Server Error")
	@ns.marshal_with(sleep_status_fields)
	def get(self):		
		sleep_status: int = get_status()
		is_sleep: bool = should_sleep_now()

		if is_sleep:
			if sleep_status == SLEEP_STATUS_AWAKE:
				set_status(SLEEP_STATUS_SLEEP)
				
		else:
			if sleep_status == SLEEP_STATUS_SLEEP:
				set_status(SLEEP_STATUS_AWAKE)
		
		sleep_status = get_status()
		return { "isSleep": True if sleep_status == SLEEP_STATUS_SLEEP else False}, 200
	

@ns.route("/create")
class scheduleCreateRes(Resource):
	@admin_required
	@ns.response(204, "")
	@ns.response(400, "Bad Request")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(500, "Internal Server Error")
	@ns.expect(schedule_create_fields, validate=True)
	def post(self):
		data: dict = ns.payload
		
		create_schedule(data)

		return "", 204


@ns.route("/<int:id>")
@ns.param("id", "Schedule ID")
class ScheduleRes(Resource):
	@admin_required
	@ns.response(204, "")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "Missing or invalid ID")
	@ns.response(500, "Internal Server Error")
	def delete(self, id: int):
		delete_schedule(id)
		return "", 204

	@admin_required
	@ns.response(204, "")
	@ns.response(400, "Bad Request")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "Missing or invalid ID")
	@ns.response(500, "Internal Server Error")
	@ns.expect(schedule_update_fields, validate=True)
	def patch(self, id: int):
		data = ns.payload
		update_schedule(id, data)
		return "", 204
