from logging import Logger, getLogger
from typing import Any

from flask import request, session
from werkzeug.security import check_password_hash
from flask_restx import Resource

from . import ns
from .model import UserModel
from app.auth.logic import react_login_required

logger: Logger = getLogger(__name__)

"""
API
"""

@ns.route("/login")
class LoginRes(Resource):
	def post(self) -> dict:
		d: dict = request.get_json()
		res: dict = {}

		username: str | None = d.get("username")
		password: str | None = d.get("password")
		if username is None or password is None:
			session["user"] = None
			res["message"] = "Username or password cannot be empty"

			return res, 401

		acct: Any | None = UserModel.query.filter_by(username=username).first()
		if acct is None or not check_password_hash(acct.password, password):
			session["user"] = None
			res["message"] = "Unknown username or password"

			return res, 401

		session["user"] = {
			"username": acct.username,
			"display_name": acct.display_name
       	}
		res["message"] = "Login successful"
		res["user"] = session["user"]

		return res, 200


@ns.route("/logout")
class LogoutRes(Resource):
	@react_login_required
	def post(self) -> dict:
		session.clear()
		res: dict = {}

		return res, 200
