from logging import Logger, getLogger
from typing import Any

from flask_restx import Resource

from app.lib.decorators import admin_required, login_required
from app.user.logic import create_user, delete_user, get_all_users, update_user

from . import ns
from .fields import *
from .models import *


logger: Logger = getLogger(__name__)

"""
API
"""

@ns.route("")
class UserListRes(Resource):
	@login_required
	@ns.response(200, "Success", model=[user_fields])
	@ns.marshal_with(user_fields, as_list=True)
	def get(self):
		all_users: list[dict] = get_all_users()
		return all_users, 200


@ns.route("/<int:user_id>")
@ns.param("user_id", "User ID")
class UserRes(Resource):
	@admin_required
	@ns.response(204, "Success")
	def delete(self, user_id: int):
		delete_user(user_id)
		
		return "", 204
	
	@login_required
	@ns.response(204, "Success")
	@ns.expect(user_update_model, validate=True)
	def patch(self, user_id: int):
		data = ns.payload
		
		update_user(user_id, data)
		
		return "", 204


@ns.route("/create")
class UserCreateRes(Resource):
	@admin_required
	@ns.expect(user_create_model, validate=True)
	@ns.response(200, "Success", user_fields)
	@ns.marshal_with(user_fields)
	def post(self):
		data = ns.payload
		
		user: dict = create_user(data)
		
		return user, 200


