from flask_restx import fields

from . import ns

queue_model = ns.model("Queue", {
	"queue": fields.List(fields.Integer, description="List of wallpaper IDs"),
})

queue_select_model = ns.model("QueueSelect", {
	"id": fields.Integer(required=True, description="Choosen wallpaper ID")
})
