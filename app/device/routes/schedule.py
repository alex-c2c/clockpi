from logging import Logger, getLogger

from flask import session
from flask_restx import Resource

from app.consts import SleepStatus
from app.lib.decorators import login_required, admin_required
from app.schedule.logic import create_schedule, update_schedule, delete_schedule, get_schedules, get_status, set_status, should_sleep_now

from .. import ns
from ..fields import *
from ..fields.schedule import *


logger: Logger = getLogger(__name__)


@ns.route("/<int:device_id>/schedule/create")
class scheduleCreateRes(Resource):
	@login_required
	@ns.response(204, "Success")
	@ns.expect(schedule_create_fields, validate=True)
	def post(self, device_id: int):
		user_id: int = session.get("id", 0)
		payload: dict = ns.payload
		
		create_schedule(user_id,device_id, payload)

		return "", 204
		

@ns.route("/schedule/<int:schedule_id>")
@ns.param("id", "Schedule ID")
class ScheduleRes(Resource):
	@admin_required
	@ns.response(204, "Success")
	def delete(self, schedule_id: int):
		user_id: int = session.get("id", 0)
		
		delete_schedule(user_id, schedule_id)
		
		return "", 204
		
	@admin_required
	@ns.response(204, "Success")
	@ns.expect(schedule_update_fields, validate=True)
	def patch(self, schedule_id: int):
		user_id: int = session.get("id", 0)
		payload = ns.payload
		
		update_schedule(user_id, schedule_id, payload)
		
		return "", 204


@ns.route("/<int:device_id>/schedules")
class DeviceScheduleListRes(Resource):
	@login_required
	@ns.response(200, "Success", [schedule_fields])
	@ns.marshal_with(schedule_fields, as_list=True)
	def get(self, device_id: int):
		user_id: int = session.get("id", 0)
		
		schedules: list[dict] = get_schedules(user_id, device_id)
		
		return schedules, 200	


@ns.route("/<int:device_id>/sleep-status")
class DeviceSleepStatusRes(Resource):
	@login_required
	@ns.response(200, "Success", sleep_status_fields)
	@ns.marshal_with(sleep_status_fields)
	def get(self, device_id: int):		
		user_id: int = session.get("id", 0)
		
		sleep_status: SleepStatus = get_status(user_id, device_id)
		is_sleep: bool = should_sleep_now(user_id, device_id)
		
		logger.debug(f"{sleep_status=} {is_sleep=}")
		
		if is_sleep:
			if sleep_status == SleepStatus.AWAKE:
				set_status(user_id, device_id, SleepStatus.SLEEP)
				
		else:
			if sleep_status == SleepStatus.SLEEP:
				set_status(user_id, device_id, SleepStatus.AWAKE)
		
		sleep_status = get_status(user_id, device_id)
		
		return { "isSleep": True if sleep_status == SleepStatus.SLEEP else False}, 200
