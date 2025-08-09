from flask_restx import fields
from numpy import require

from . import ns

user_field = ns.model("User", {
	"username": fields.String(required=True),
	"dispName": fields.String(required=True),
	"role": 	fields.String(required=True)
})

user_create_field = ns.model("UserCreate", {
	"username":		 	fields.String(required=True),
	"dispName": 		fields.String(required=True),
	"password": 		fields.String(required=True),
	"confirmPassword": 	fields.String(required=True),
	"role": 			fields.String(required=True)
})
