from logging import Logger, getLogger

from flask import session
from flask_restx import Resource

from . import ns
from .fields import *
from app.auth.logic import login_required, login_user

logger: Logger = getLogger(__name__)

"""
API
"""

@ns.route("/login")
class LoginRes(Resource):
	@ns.response(204, "")
	@ns.response(400, "Bad Request")
	@ns.response(401, "Authentication Error")
	@ns.expect(login_field)
	def post(self):
		data = ns.payload
		login_user(data)
		
		return "", 204


@ns.route("/logout")
class LogoutRes(Resource):
	@login_required
	@ns.response(204, "")
	@ns.response(401, "Authentication Error")
	def post(self):
		session.clear()

		return "", 204
