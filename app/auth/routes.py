from logging import Logger, getLogger

from flask_restx import Resource

from app.auth.logic import login_user
from app.lib.errors import error_fields
from app.session_pkg.logic import clear_session
from app.user.fields import user_fields

from . import ns
from .fields import *

logger: Logger = getLogger(__name__)

"""
API
"""

@ns.route("/login")
class LoginRes(Resource):
	@ns.expect(login_fields)
	@ns.response(200, "Success", user_fields)
	@ns.response(400, "Bad Request", error_fields)
	@ns.marshal_with(user_fields)
	def post(self):
		data = ns.payload
		
		user: dict = login_user(data)
		
		return user, 200


@ns.route("/logout")
class LogoutRes(Resource):
	@ns.response(204, "")
	def post(self):
		clear_session()

		return "", 204
