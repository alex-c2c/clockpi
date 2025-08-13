from flask_restx import fields

from . import ns

sleep_fields = ns.model("Sleep", {
	"id":			fields.Integer(description="Sleep schedule ID", readyOnly=True),
	"days":		 	fields.List(fields.String, default=["mon", "tue", "wed", "thu", "fri", "sat", "sun"], description="Days of week (Case insensitive)"),
	"startTime": 	fields.String(description="Start time, 24hr format", default="HH:MM"),
	"duration":		fields.Integer(description="Duration of sleep, 1 <= duration <= 1440"),
	"isEnabled":	fields.Boolean(description="Enable this schedule")
})

sleep_list_fields = ns.model("SleepList", {
	"sleepList":	fields.List(fields.Nested(sleep_fields), description="List of sleep fields")
})

sleep_status_fields = ns.model("SleepStatus", {
	"isSleep": fields.Boolean(description="Is sleeping?")
})

sleep_create_fields = ns.model("SleepCreate", {
	"days":		 	fields.List(fields.String, default=["mon", "tue", "wed", "thu", "fri", "sat", "sun"], description="Days of week (Case insensitive), can be empty", required=True),
	"startTime": 	fields.String(description="Start time, 24hr format", default="HH:MM", required=True),
	"duration":		fields.Integer(description="Duration of sleep, 1 <= duration <= 1440", required=True),
	"isEnabled":	fields.Boolean(description="Enable this schedule", required=True)
})

sleep_update_fields = ns.model("SleepUpdate", {
	"days":		 	fields.List(fields.String, default=["mon", "tue", "wed", "thu", "fri", "sat", "sun"], description="Days of week (Case insensitive), can be empty"),
	"startTime": 	fields.String(description="Start time, 24hr format", default="HH:MM"),
	"duration":		fields.Integer(description="Duration of sleep, 1 <= duration <= 1440"),
	"isEnabled":	fields.Boolean(description="Enable this schedule")
})
