from logging import Logger, getLogger

from flask import session
from flask_restx import Resource

from app.lib.decorators import login_required
from app.lib.errors import api_abort, ErrorCode

from .. import ns
from ..fields import *
from ..logic import can_access_device, create_device, get_device, get_devices, update_device, delete_device


logger: Logger = getLogger(__name__)


"""
API
"""


@ns.route("")
class DeviceListRes(Resource):
	@login_required
	@ns.response(200, "Success", [device_fields])
	@ns.marshal_with(device_fields, as_list=True)
	def get(self):
		user_id: int = session.get("userId", 0)
		devices: list[dict] = get_devices(user_id)
		
		return devices, 200
	
	
@ns.route("/create")
class DeviceCreateRes(Resource):
	@login_required
	@ns.expect(device_create_fields, validate=True)
	@ns.response(200, "Success", device_fields)
	@ns.marshal_with(device_fields)
	def post(self):
		user_id: int = session.get("userId", 0)
		payload: dict = ns.payload

		device: dict = create_device(user_id, payload)
		
		return device, 200


@ns.route("/<int:device_id>")
@ns.param("device_id", "Device ID")
class DeviceRes(Resource):
	@login_required
	@ns.response(200, "Success", device_fields)
	def get(self, device_id: int):
		user_id: int = session.get("userId", 0)

		if not can_access_device(user_id, device_id):
			api_abort(ErrorCode.FORBIDDEN)
		
		device: dict = get_device(user_id, device_id)
			
		return device, 200
		
			
	@login_required
	@ns.expect(device_update_fields, validate=True)
	@ns.response(200, "Success", device_fields)
	def patch(self, device_id: int):
		payload = ns.payload
		user_id: int = session.get("userId", 0)
		
		if not can_access_device(user_id, device_id):
			api_abort((ErrorCode.FORBIDDEN))
		
		device: dict = update_device(user_id, device_id, payload)		

		return device, 200
	
	
	@login_required
	@ns.response(204, "Success")
	def delete(self, device_id: int):
		user_id: int = session.get("userId", 0)
		
		if not can_access_device(user_id, device_id):
			api_abort(ErrorCode.FORBIDDEN)

		delete_device(device_id)

		return "", 204
