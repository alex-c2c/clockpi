import getpass
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
from logging import Logger, getLogger
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.auth.logic import is_password_valid, is_username_valid
from app.models import AccountModel


bp: Blueprint = Blueprint("auth", __name__, url_prefix="/auth")
logger: Logger = getLogger(__name__)


@bp.cli.command("createsuperuser")
def createsuperuser() -> None:
	username: str = str(input(f"Username: "))
	if not is_username_valid(username):
		print(f"[ERROR] Unable to create super user")
		return

	password: str = getpass(f"Password: ")
	if not is_password_valid(password):
		print(f"[ERROR] Unable to create super user")
		return

	new_acct: AccountModel = AccountModel(username, generate_password_hash(password))
	db.session.add(new_acct)
	db.session.commit()

	print(f"Created super user {username=}")


@bp.route("/login", methods=("GET", "POST"))
def login():
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
			session.clear()
			session["acct_id"] = acct.id
			return redirect(url_for("index"))

		flash(error)

	return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
	logger.debug(f"load_logged_in_user")
	acct_id = session.get("acct_id")

	if acct_id is None:
		g.user = None
	else:
		g.user = AccountModel.query.get(acct_id)


@bp.route("/logout")
def logout():
	session.clear()
	return redirect(url_for("index"))
