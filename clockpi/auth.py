from getpass import getpass
import functools
import re

from logging import Logger, getLogger
from flask import (
	Blueprint,
	flash,
	g,
	redirect,
	render_template,
	request,
	session,
	url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from clockpi.db import get_db


bp = Blueprint("auth", __name__, url_prefix="/auth")
logger: Logger = getLogger(__name__)


USERNAME_MIN_LEN: int = 4
USERNAME_MAX_LEN: int = 32
USERNAME_REGEX: str = r"^[A-Za-z][A-Za-z0-9_]*$"
PASSWORD_MIN_LEN: int = 16


def is_username_valid(username: str) -> bool:
	if len(username) < USERNAME_MIN_LEN or len(username) > USERNAME_MAX_LEN:
		print(
			f"[ERROR] Username's length needs to be between {USERNAME_MIN_LEN} and {USERNAME_MAX_LEN}"
		)
		return False

	if not bool(re.match(USERNAME_REGEX, username)):
		print(f"[ERROR] Username failed regex check")
		return False

	return True


def is_password_valid(password: str) -> bool:
	if len(password) < PASSWORD_MIN_LEN:
		print(
			f"[ERROR] Password needs to be at least {PASSWORD_MIN_LEN} character long"
		)
		return False

	if not re.search(r"[A-Z]", password):
		print(f"[ERROR] Password needs to contain at least one capital letter")
		return False

	if not re.search(r"[a-z]", password):
		print(f"[ERROR] Password needs to contain at least one small case letter")
		return False

	if not re.search(r"[0-9]", password):
		print(f"[ERROR] Password needs to contain at least one number")
		return False

	if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
		print(f"[ERROR] Password needs to contain at least one special character")
		return False

	return True


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

	db = get_db()
	db.execute(
		"INSERT INTO user (username, password) VALUES (?, ?)",
		(username, generate_password_hash(password)),
	)
	db.commit()

	print(f"Created super user {username=}")


"""
@bp.route("/register", methods=("GET", "POST"))
def register():
	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		db = get_db()
		error = None

		if not username:
			error = "Username is required."
		elif not password:
			error = "Password is required."

		if error is None:
			try:
				db.execute(
					"INSERT INTO user (username, password) VALUES (?, ?)",
					(username, generate_password_hash(password)),
				)
				db.commit()
			except db.IntegrityError:
				error = f"User {username} is already registered."
			else:
				return redirect(url_for("auth.login"))

		flash(error)

	return render_template("auth/register.html")
"""


@bp.route("/login", methods=("GET", "POST"))
def login():
	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		db = get_db()
		error = None
		user = db.execute(
			"SELECT * FROM user WHERE username = ?", (username,)
		).fetchone()

		if user is None:
			error = "Incorrect username."
		elif not check_password_hash(user["password"], password):
			error = "Incorrect password."

		if error is None:
			session.clear()
			session["user_id"] = user["id"]
			return redirect(url_for("index"))

		flash(error)

	return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
	user_id = session.get("user_id")

	if user_id is None:
		g.user = None
	else:
		g.user = (
			get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
		)


@bp.route("/logout")
def logout():
	session.clear()
	return redirect(url_for("index"))


def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for("auth.login"))

		return view(**kwargs)

	return wrapped_view
