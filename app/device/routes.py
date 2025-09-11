from logging import Logger, getLogger

from flask import session
from flask_restx import Resource

from app.consts import SleepStatus
from app.lib.decorators import login_required
from app.schedule.fields import schedule_fields, schedule_create_fields
from app.schedule.logic import create_schedule, get_schedules, get_status, set_status, should_sleep_now
from app.wallpaper.fields import wallpaper_fields
from app.wallpaper.logic import get_wallpapers

from . import ns
from .fields import *
from .logic import create_device, get_device, get_devices, update_device, delete_device
from .logic.display import clear_display, update_display
from .logic.queue import move_to_first, shift_next, shuffle_queue


logger: Logger = getLogger(__name__)


"""
API
"""


@ns.route("")
class DeviceListRes(Resource):
	@login_required
	@ns.response(200, "Success", [device_fields])
	@ns.response(401, "Unauthenticated error")
	@ns.marshal_with(device_fields, as_list=True)
	def get(self):
		user_id: int = session.get("id", 0)
		
		devices: list[dict] = get_devices(user_id)
		
		return devices, 200
	
	
@ns.route("/create")
class DeviceCreateRes(Resource):
	@login_required
	@ns.expect(device_create_fields)
	@ns.response(200, "Success", device_fields)
	@ns.response(400, "Bad request")
	@ns.response(401, "Unauthenticated error")
	@ns.response(403, "Unauthorized error")
	@ns.response(500, "Internal server error")
	@ns.marshal_with(device_fields)
	def post(self):
		user_id: int = session.get("id", 0)
		payload: dict = ns.payload

		device: dict = create_device(user_id, payload)
		
		return device, 200


@ns.route("/<int:device_id>")
@ns.param("device_id", "Device ID")
class DeviceRes(Resource):
	@login_required
	@ns.response(200, "Success", device_fields)
	@ns.response(400, "Bad Request")
	@ns.response(401, "Unauthenticated error")
	@ns.response(403, "Unauthorized error")
	@ns.response(404, "Resource not found")
	@ns.response(500, "Internal server error")
	def get(self, device_id: int):
		user_id: int = session.get("id", 0)
		
		device: dict = get_device(user_id, device_id)
			
		return device, 200
		
			
	@login_required
	@ns.expect(device_update_fields)
	@ns.response(200, "Success", device_fields)
	@ns.response(400, "Bad Request")
	@ns.response(401, "Unauthenticated error")
	@ns.response(403, "Unauthorized error")
	@ns.response(404, "Resource not found")
	@ns.response(500, "Internal server error")
	def patch(self, device_id: int):
		payload = ns.payload
		user_id: int = session.get("id", 0)
		
		device: dict = update_device(user_id, device_id, payload)		

		return device, 200
	
	
	@login_required
	@ns.response(204, "Success")
	@ns.response(401, "Unauthenticated error")
	@ns.response(403, "Unauthorized error")
	@ns.response(404, "Resource not found")
	@ns.response(500, "Internal server error")
	def delete(self, device_id: int):
		user_id: int = session.get("id", 0)

		delete_device(user_id, device_id)

		return "", 204
	

@ns.route("/<int:device_id>/display/clear")
@ns.param("device_id", "Device ID")
class DeviceDisplayClearRes(Resource):
	@login_required
	@ns.response(204, "Success")
	@ns.response(401, "Unauthenticated error")
	@ns.response(403, "Unauthorized error")
	@ns.response(404, "Resource not found")
	def get(self, device_id: int):
		user_id: int = session.get("id", 0)
		
		clear_display(user_id, device_id)
		
		return "", 204


@ns.route("/<int:device_id>/display/refresh")
@ns.param("device_id", "Device ID")
class DeviceDisplayRefreshRes(Resource):
	@login_required
	@ns.response(204, "Success")
	@ns.response(401, "Unauthenticated error")
	@ns.response(403, "Unauthorized error")
	@ns.response(404, "Resource not found")
	def get(self, device_id: int):
		user_id: int = session.get("id", 0)
		
		update_display(user_id, device_id)
		
		return "", 204


@ns.route("/<int:device_id>/queue/shuffle")
class DeviceQueueShuffleRes(Resource):
	@login_required
	@ns.response(204, "Success")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(500, "Internal Server Error")
	def get(self, device_id: int):
		user_id: int = session.get("id", 0)

		shuffle_queue(user_id, device_id)
		
		return "", 204


@ns.route("/<int:device_id>/queue/next")
class DeviceQueueNextRes(Resource):
	@login_required
	@ns.response(204, "Success")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(500, "Internal Server Error")
	def get(self, device_id: int):
		user_id: int = session.get("id", 0)
		
		shift_next(user_id, device_id)
		
		return "", 204


@ns.route("/<int:device_id>/queue/select")
class DeviceQueueSelectRes(Resource):
	@login_required
	@ns.response(204, "Success")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "ID not found")
	@ns.response(500, "Internal Server Error")
	@ns.expect(device_queue_select_fields, validate=True)
	def patch(self, device_id: int):
		user_id: int = session.get("id", 0)
		payload: dict = ns.payload
		
		move_to_first(user_id, device_id, payload.get("wallpaperId", 0))
		
		return "", 204
		

@ns.route("/<int:device_id>/schedule/create")
class scheduleCreateRes(Resource):
	@login_required
	@ns.response(204, "")
	@ns.response(400, "Bad Request")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(500, "Internal Server Error")
	@ns.expect(schedule_create_fields, validate=True)
	def post(self, device_id: int):
		user_id: int = session.get("id", 0)
		payload: dict = ns.payload
		
		create_schedule(user_id,device_id, payload)

		return "", 204


@ns.route("/<int:device_id>/wallpapers")
class DeviceWallpaperListRes(Resource):
	@login_required
	@ns.response(200, "Success")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "Resource not found")
	@ns.marshal_with(wallpaper_fields, as_list=True)
	def get(self, device_id: int):
		user_id: int = session.get("id", 0)
		
		wallpapers: list[dict] = get_wallpapers(user_id, device_id)
		
		return wallpapers, 200


@ns.route("/<int:device_id>/schedules")
class DeviceScheduleListRes(Resource):
	@login_required
	@ns.response(200, "Success", [device_schedule_fields])
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "Resource not found")
	@ns.marshal_with(device_schedule_fields, as_list=True)
	def get(self, device_id: int):
		user_id: int = session.get("id", 0)
		
		schedules: list[dict] = get_schedules(user_id, device_id)
		
		return schedules, 200	


@ns.route("/<int:device_id>/sleep-status")
class DeviceSleepStatusRes(Resource):
	@login_required
	@ns.response(200, "Success", device_sleep_fields)
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(500, "Internal Server Error")
	@ns.marshal_with(device_sleep_fields)
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
