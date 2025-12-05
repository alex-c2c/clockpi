from flask_restx import Resource

from app.lib.decorators import local_apikey_required

from . import ns
from .logic import shift_all_device_queue, shift_device_queue, shuffle_all_device_queue, shuffle_device_queue, tick_all_devices, tick_device

@ns.route("/tick-all")
class TickAllDeviceRes(Resource):
	@local_apikey_required
	@ns.response(204, "Success")
	def post(self):
		
		tick_all_devices()
		
		return "", 204
		

@ns.route("/tick/<int:device_id>")
@ns.param("device_id", "Device ID")
class TickDeviceRes(Resource):
	@local_apikey_required
	@ns.response(204, "Success")
	def post(self, device_id: int):
		data = ns.payload
		
		tick_device(device_id)
		
		return "", 204


@ns.route("/next-all")
class ShiftAllDeviceRes(Resource):
	@local_apikey_required
	@ns.response(204, "Success")
	def post(self):
		
		shift_all_device_queue()
		
		return "", 204
		
@ns.route("/next/<int:device_id>")
@ns.param("device_id", "Device ID")
class ShiftDeviceRes(Resource):
	@local_apikey_required
	@ns.response(204, "Success")
	def post(self, device_id: int):
		data = ns.payload
		
		shift_device_queue(device_id)
		
		return "", 204
		
		
@ns.route("/shuffle-all")
class ShuffleAllRes(Resource):
	@local_apikey_required
	@ns.response(204, "Success")
	def post(self):
		
		shuffle_all_device_queue()
		
		return "", 204


@ns.route("/shuffle/<int:device_id>")
@ns.param("device_id", "Device ID")
class ShuffleDeviceRes(Resource):
	@local_apikey_required
	@ns.response(204, "Success")
	def post(self, device_id: int):
		data = ns.payload
		
		shuffle_device_queue(device_id)
		
		return "", 204
