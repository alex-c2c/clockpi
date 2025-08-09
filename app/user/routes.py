from logging import Logger, getLogger
from typing import Any

from flask import request, session
from werkzeug.security import check_password_hash
from flask_restx import Resource

from app.user.logic import get_all_users

from . import ns
from .fields import *
from .models import *

from app.auth.logic import login_required

logger: Logger = getLogger(__name__)

"""
API
"""

@ns.route("/")
class UserListRes(Resource):
	@login_required
	@ns.response(200, list[user_field])
	@ns.marshal_with(user_field, as_list=True)
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	def get(self):
		
		all_users: list[dict] = get_all_users()
		
		return all_users, 200


@ns.route("/<int:id>")
class UserRes(Resource):
	@login_required
	@ns.response(204, "")
	@ns.response(400, "Bad Request")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "User not found")
	def delete(self):
		...
		return "", 204
	
	@login_required
	@ns.response(204, "")
	@ns.response(400, "Bad Request")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "User not found")
	def patch(self):
		...
		return "", 204


@ns.route("/create")
class UserCreateRes(Resource):
	@login_required
	@ns.response(204, "")
	@ns.response(400, "Bad Request")
	@ns.response(401, "Authentication Error")
	@ns.expect(user_create_field)
	def post(self):
		...
		return "", 204


