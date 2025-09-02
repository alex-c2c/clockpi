from logging import Logger, getLogger

from flask import session
from flask_restx import Resource

from app.auth.logic import login_user
from app.session_pkg.logic import clear_session
from app.user.fields import user_model
from app.user.models import UserModel

from . import ns
from .fields import *

logger: Logger = getLogger(__name__)

"""
API
"""

@ns.route("/login")
class LoginRes(Resource):
	@ns.response(200, "", user_model)
	@ns.response(400, "Invalid username or password")
	@ns.expect(login_model)
	@ns.marshal_with(user_model)
	def post(self):
		data = ns.payload
		user: UserModel | None = login_user(data)
		
		if user is None:
			ns.abort(400, "Invalid username or password")
			return
			
		return user.to_dict(), 200


@ns.route("/logout")
class LogoutRes(Resource):
	@ns.response(204, "")
	def post(self):
		clear_session()

		return "", 204
