from flask_restx import fields

from app.user.consts import UserRole

from . import ns

user_model = ns.model("User", {
	"id":			fields.Integer(description="User ID"),
	"username": 	fields.String(description="User name"),
	"dispName": 	fields.String(description="User's display name"),
	"role": 		fields.String(description="User's access role", enum=[f"{UserRole.ADMIN.value}, {UserRole.USER.value}, {UserRole.VIEWER.value}"])
})

user_list_model = ns.model("UserList", {
	"users": fields.List(fields.Nested(user_model))
})

user_create_model = ns.model("UserCreate", {
	"username":		 		fields.String(required=True, description="User name"),
	"dispName": 			fields.String(required=True, description="User's display name"),
	"password": 			fields.String(required=True, description="User's password"),
	"confirmPassword": 		fields.String(required=True, description="User's password (confirmation)"),
	"role": 				fields.String(required=True, description="User's access role", enum=[f"{UserRole.ADMIN.value}, {UserRole.USER.value}, {UserRole.VIEWER.value}"])
})

user_update_model = ns.model("UserUpdate", {
	"dispName":				fields.String(description="User's display name"),
	"currentPassword": 		fields.String(description="User's current password"),
	"newPassword":			fields.String(description="User's new password"),
	"newConfirmPassword":	fields.String(description="User's new password (confirmation)"),
	"role":					fields.String(description="User's access role", enum=[f"{UserRole.ADMIN.value}, {UserRole.USER.value}, {UserRole.VIEWER.value}"])
})
