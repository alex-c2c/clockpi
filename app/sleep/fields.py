from flask_restx import fields

from . import ns

sleep_model = ns.model("Sleep", {
	"id":			fields.Integer(required=True),
	"days":		 	fields.List(fields.String, required=True),
	"startTime": 	fields.String(required=True),
	"duration":		fields.Integer(required=True),
	"isEnabled":	fields.Boolean(required=True)
})

sleep_status_model = ns.model("SleepStatus", {
	"isSleep": fields.Boolean
})

sleep_create_model = ns.model("SleepCreate", {
	"days":		 	fields.List(fields.String, required=True),
	"startTime": 	fields.String(required=True),
	"duration":		fields.Integer(required=True),
	"isEnabled":	fields.Boolean(required=True)
})

sleep_update_model = ns.model("SleepUpdate", {
	"days":		 	fields.List(fields.String),
	"startTime": 	fields.String(),
	"duration":		fields.Integer(),
	"isEnabled":	fields.Boolean()
})
