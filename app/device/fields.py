from flask_restx import fields

from . import ns
from .consts import Orientation

device_fields = ns.model("Device", {
	"id":					fields.Integer(description="Device ID", readyOnly=True),
	"name":					fields.String(description="Device name"),
	"desc":					fields.String(description="Description"),
	"ipv4":					fields.String(description="Device IP address"),
	"type":					fields.String(description="Device type"),
	"supportedColors":		fields.List(fields.String, description="List of supported colors", readOnly=True),
	"defaultLabelColor": 	fields.String(description="Default label color", readOnly=True),
	"defaultLabelShadow": 	fields.String(description="Default label shadow", readOnly=True),
	"orientation":			fields.String(description="Screen orientation", enum=[f"{Orientation.HORIZONTAL.value, {Orientation.VERTICAL.value}}"], default=Orientation.HORIZONTAL.value),
	"width":				fields.Integer(description="Screen width", readOnly=True),
	"height":				fields.Integer(description="Screen height", readOnly=True),
	"queue":				fields.List(fields.Integer, description="List of wallpaper IDs", readOnly=True),
	"isDrawGrid":			fields.Boolean(description="Is draw grid on screen?"),
	"isSleep":				fields.Boolean(description="Is device sleeping?", readOnly=True),
	"isEnabled":			fields.Boolean(description="Is device enabled?"),
})

device_update_fields = ns.model("DeviceUpdate", {
	"name":			fields.String(description="Device name"),
	"desc":			fields.String(description="Description"),
	"ipv4":			fields.String(description="Device IP address"),
	"type":			fields.String(description="Device type"),
	"orientation":	fields.String(description="Screen orientation"),
	"isDrawGrid":	fields.Boolean(description="Is draw grid on screen?"),
	"isEnabled":	fields.Boolean(description="Is device enabled?"),	
})

device_create_fields = ns.model("DeviceCreate", {
	"name":			fields.String(description="Device name", required=True),
	"desc":			fields.String(description="Description"),
	"ipv4":			fields.String(description="Device IP address", required=True),
	"type":			fields.String(description="Device type", required=True),
	"orientation":	fields.String(description="Screen orientation", required=True),
})

device_sleep_fields = ns.model("DeviceSleep", {
	"isSleep":		fields.Boolean(description="Is device sleeping?", readOnly=True),
})

device_queue_select_fields = ns.model("DeviceQueueSelect", {
	"wallpaperId": fields.Integer(required=True, description="Choosen wallpaper ID")
})

device_schedule_fields = ns.model("DeviceSchedule", {
	"id":			fields.Integer(description="Schedule ID", readyOnly=True),
	"days":		 	fields.List(fields.String, default=["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"], description="Days of week (Case sensitive)"),
	"startTime": 	fields.String(description="Start time, 24hr format", default="HH:MM"),
	"duration":		fields.Integer(description="Duration of sleep, 1 <= duration <= 1440"),
	"isEnabled":	fields.Boolean(description="Enable this schedule")
})
