from flask_restx import fields

from . import ns

session_model = ns.model("Session", {
	"id": fields.Integer(dsecription="User ID"),
	"username": fields.String(dsecription="User name"),
	"dispName": fields.String(description="User's display name"),
	"role": fields.String(description="User's access role")	
})
