from typing import Any
from flask import (
	flash,
	Blueprint,
	g,
	redirect,
	render_template,
	request,
	session,
	url_for,
)
from werkzeug.security import check_password_hash
from flask_restx import Namespace, Resource

from app import api_v1
from app.auth.logic import react_login_required
from . import logger
from app.models import AccountModel


bp: Blueprint = Blueprint("auth", __name__, url_prefix="/auth")
ns: Namespace = api_v1.namespace("auth", description="Authentication operations")


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

		acct: Any | None = AccountModel.query.filter_by(username=username).first()
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


@ns.route("/session")
class SessionRes(Resource):
	def get(self) -> dict:
		logger.debug(f"{session=}")
		user: Any | None = session.get("user")
		res: dict = {}

		if user is None:
			res["message"] = "Missing session"
			return res, 401

		res["message"] = ""
		res["user"] = user
		return res, 200
