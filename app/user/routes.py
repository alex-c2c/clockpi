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
	@ns.response(200, "Success", model=user_fields)
	@ns.response(401, "Authentication Error")
	@ns.marshal_with(user_fields, as_list=True)
	def get(self):
		all_users: list[dict] = get_all_users()
		return all_users, 200


@ns.route("/<int:id>")
@ns.param("id", "User ID")
class UserRes(Resource):
	@admin_required
	@ns.response(204, "")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "User resource not found")
	@ns.response(500, "Internal Server Error")
	def delete(self, id: int):
		delete_user(id)
		return "", 204
	
	@login_required
	@ns.response(204, "")
	@ns.response(400, "Bad Request")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "User resource not found")
	@ns.response(500, "Internal Server Error")
	@ns.expect(user_update_model, validate=True)
	def patch(self, id: int):
		data = ns.payload
		update_user(id, data)
		return "", 204


@ns.route("/create")
class UserCreateRes(Resource):
	@admin_required
	@ns.response(204, "")
	@ns.response(400, "Bad Request")
	@ns.response(401, "Authentication Error")
	@ns.response(409, "Duplicate username")
	@ns.response(500, "Internal Server Error")
	@ns.expect(user_create_model, validate=True)
	def post(self):
		data = ns.payload
		create_user(data)
		return "", 204


