from logging import Logger, getLogger

from flask import session
from flask_restx import Resource

from . import ns
from .fields import *
from app.auth.logic import login_user

logger: Logger = getLogger(__name__)

"""
API
"""

@ns.route("/login")
class LoginRes(Resource):
	@ns.response(204, "")
	@ns.response(400, "Invalid username or password")
	@ns.expect(login_model)
	def post(self):
		data = ns.payload
		login_user(data)
		
		return "", 204


@ns.route("/logout")
class LogoutRes(Resource):
	@ns.response(204, "")
	def post(self):
		session.clear()

		return "", 204
