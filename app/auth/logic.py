import functools
import re

from flask import g, redirect, url_for
from logging import Logger, getLogger

from app.consts import *


logger: Logger = getLogger(__name__)


def is_username_valid(username: str) -> bool:
	if len(username) < USERNAME_MIN_LEN or len(username) > USERNAME_MAX_LEN:
		logger.error(
			f"[ERROR] Username's length needs to be between {USERNAME_MIN_LEN} and {USERNAME_MAX_LEN}"
		)
		return False

	if not bool(re.match(USERNAME_REGEX, username)):
		print(f"[ERROR] Username failed regex check")
		return False

	return True


def is_password_valid(password: str) -> bool:
	if len(password) < PASSWORD_MIN_LEN:
		logger.error(
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


def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for("auth.view_login"))

		return view(**kwargs)

	return wrapped_view
