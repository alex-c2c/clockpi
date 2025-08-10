from flask_restx import fields

from . import ns

user_model = ns.model("User", {
	"id":		fields.Integer(required=True),
	"username": fields.String(required=True),
	"dispName": fields.String(required=True),
	"role": 	fields.String(required=True)
})

user_create_model = ns.model("UserCreate", {
	"username":		 	fields.String(required=True),
	"dispName": 		fields.String(required=True),
	"password": 		fields.String(required=True),
	"confirmPassword": 	fields.String(required=True),
})

user_update_model = ns.model("UserUpdate", {
	"dispName":				fields.String,
	"currentPassword": 		fields.String,
	"newPassword":			fields.String,
	"newConfirmPassword":	fields.String,
	"role":					fields.String
})
