from flask_restx import fields

from . import ns

login_model = ns.model("Login", {
	"username": fields.String(required=True, description="User name"),
	"password": fields.String(required=True, description="User password")
})
