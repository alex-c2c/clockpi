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

from . import logger
from app.models import AccountModel


bp: Blueprint = Blueprint("auth", __name__, url_prefix="/auth")


"""
Blueprints
"""


@bp.route("/login", methods=("GET", "POST"))
def view_login():
	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		error = None
		acct = AccountModel.query.filter_by(username=username).first()

		if acct is None:
			error = "Incorrect username."
		elif not check_password_hash(acct.password, password):
			error = "Incorrect password."

		if error is None:
			session["username"] = acct.username
			return redirect(url_for("main.view_index"))
		else:
			session["username"] = None

		flash(error)
		
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
