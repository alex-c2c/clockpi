from flask_restx import fields

from . import ns

queue_select_fields = ns.model("QueueSelect", {
	"id": fields.Integer(required=True, description="Choosen wallpaper ID")
})
