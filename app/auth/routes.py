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
from . import logger
from app.models import AccountModel


bp: Blueprint = Blueprint("auth", __name__, url_prefix="/auth")
ns: Namespace = api_v1.namespace("auth", description="Authentication operations")


"""
API
"""


@ns.route("/login")
class LoginRes(Resource):
	def get(self) -> dict:
		d: dict = request.get_json()
		username: str | None = d.get("username")
		password: str | None = d.get("password")
		error = None
		acct: Any | None = AccountModel.query.filter_by(username=username).first()

		if acct is None:
			error = "Incorrect username."
		elif not check_password_hash(acct.password, password):
			error = "Incorrect password."

		if error is not None:
			session["username"] = None
			return error, 403

		session["username"] = acct.username
  
		logger.info(msg=str(session))
  
		return "", 204


"""
Blueprints
"""


@bp.route("/login", methods=("GET", "POST"))
def view_login():
	if session.get("username") is not None:
		return redirect(url_for("main.view_index"))
    
	if request.method == "POST":
		username: str = request.form["username"]
		password: str = request.form["password"]
		error: str | None = None
		acct: Any | None = AccountModel.query.filter_by(username=username).first()

		if acct is None:
			error = "Incorrect username."
		elif not check_password_hash(acct.password, password):
			error = "Incorrect password."

		if error is not None:
			session["username"] = None
			flash(error)
			return render_template("auth/login.html")

		session["username"] = acct.username
		return redirect(url_for("main.view_index"))
 
	return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
	username: str | None = session.get("username")
	if username is not None or username != "":
		acct = AccountModel.query.filter_by(username=username).first()
		if acct is not None:
			g.user = acct.username
			return

	g.user = None


@bp.route("/logout")
def view_logout():
	session.clear()
	return redirect(url_for("main.view_index"))
