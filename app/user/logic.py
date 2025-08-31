import re
import sys

from logging import Logger, getLogger

from werkzeug.security import generate_password_hash, check_password_hash

from . import ns
from .consts import *

from app import db
from app.session_pkg.logic import get_user_from_session
from app.user.models import UserModel

logger: Logger = getLogger(__name__)

"""""
LOGIC
""" ""


def is_username_valid(username: str) -> bool:
	regex = re.compile(USERNAME_REGEX)
	return bool(regex.match(username))


def is_password_valid(password: str) -> bool:
	regex = re.compile((PASSWORD_REGEX))
	return bool(regex.match(password))


def is_disp_name_valid(disp_name: str) -> bool:
	regex = re.compile(DISP_NAME_REGEX)
	return bool(regex.match(disp_name))


def get_all_users() -> list[dict]:
	data: list[UserModel] = db.session.query(UserModel).all()
	return [user.to_dict() for user in data]


def create_user(data: dict) -> UserModel | None:	
	username: str = data.get("username", "")
	if not is_username_valid(username):
		ns.abort(400, "Invalid username")
		return
	else:
		username = username.lower()
		
	existing_user: UserModel | None = UserModel.query.filter_by(username=username).one_or_none()
	if existing_user is not None:
		ns.abort(415, "Username has already been taken")
		return

	password: str = data.get("password", "")
	confirm_password: str = data.get("confirmPassword", "")

	if password != confirm_password or len(password) == 0:
		ns.abort(400, "Invalid password")
		return

	if not is_password_valid(password):
		ns.abort(400, "Invalid password")
		return
		
	role_str: str | None = data.get("role")
	if sys.version_info < (3, 13):
		roles: list[str] = [str(ur.value) for ur in UserRole()]
		if role_str is None or role_str not in roles:
			ns.abort(400, "Invalid role")
			return
	else:
		if role_str is None or role_str not in UserRole:
			ns.abort(400, "Invalid role")
			return
	
	disp_name: str = data.get("dispName", "")

	new_user: UserModel = UserModel(
		username,
		generate_password_hash(password),
		disp_name,
		UserRole[role_str]
	)

	try:
		db.session.add(new_user)
		db.session.commit()
	except Exception as e:
		logger.error(f"Unable to create new user with {data=} due to {e=}")
		ns.abort(500, "Internal Server Error")
		return

	logger.info(f"User {new_user.id}:{new_user.username} created")
	return new_user


def update_user(user_id: int, data: dict) -> None:
	myself: UserModel | None = get_user_from_session()
	if myself is None:
		ns.abort(401, "Authentication Error")
		return

	user: UserModel | None = db.session.get(UserModel, user_id)
	if user is None:
		ns.abort(404, "User resource not found")
		return

	current_password: str = data.get("currentPassword", "")
	new_password: str = data.get("newPassword", "")
	new_confirm_password: str = data.get("newConfirmPassword", "")
	if len(current_password) > 0:
		if not check_password_hash(user.password, current_password):
			ns.abort(401, "Current password does not match")
			return

		if new_password != new_confirm_password or len(new_password) == 0:
			ns.abort(400, "Invalid new password")
			return

		if not is_password_valid(new_password):
			ns.abort(400, "New passwords does not match")
			return

		user.password = generate_password_hash(new_password)

	disp_name: str = data.get("dispName", "")
	if len(disp_name) > 0:
		if not is_disp_name_valid(disp_name):
			ns.abort(400, "Invalid display name")
			return

		user.disp_name = disp_name

	role_str: str = data.get("role", "")
	if len(role_str) > 0:
		if role_str not in UserRole:
			ns.abort(400, "Invalid role")
			return

		if myself.role != UserRole.ADMIN:
			ns.abort(403, "Authorization Error")
			return

		user.role = UserRole[role_str]

	try:
		db.session.commit()
	except Exception as e:
		logger.error(f"Unable to save user update with {data=} due to {e=}")
		ns.abort(500, "Internal Server Error")
		return

	logger.info(f"User {user.id}:{user.username} updated")


def delete_user(user_id: int) -> None:
	user: UserModel | None = db.session.get(UserModel, user_id)
	if user is None:
		ns.abort(404, "User resource not found")
		return

	try:
		db.session.delete(user)
		db.session.commit()
	except Exception as e:
		logger.error(f"Unable to delete user {user_id=} due to {e=}")
		ns.abort(500, "Internal Server Error")
		return

	logger.info(f"User {user_id} deleted")
