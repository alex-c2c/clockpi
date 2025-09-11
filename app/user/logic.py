import re
import sys

from logging import Logger, getLogger
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.lib.errors import api_abort, ErrorCode
from app.session_pkg.logic import get_user_from_session

from .consts import *
from .models import UserModel
from .utils import *


logger: Logger = getLogger(__name__)


"""""
LOGIC
"""""


def get_all_users() -> list[dict]:
	data: list[UserModel] = db.session.query(UserModel).all()
	return [user.to_dict() for user in data]


def create_user(data: dict) -> dict:
	failed_validations: dict = {}
	
	username: str | None = data.get("username")
	if username is None:
		api_abort(ErrorCode.INVALID_INPUT, fields={"username":"This is a required field"})
		
	if (err := is_username_valid(username)) is not None:
		failed_validations["username"] = err
	
	username = username.lower()
		
	existing_user: UserModel | None = UserModel.query.filter_by(username=username).one_or_none()
	if existing_user is not None:
		api_abort(ErrorCode.CONFLICT, detail="Username already taken")

	password: str | None = data.get("password")
	confirm_password: str | None = data.get("confirmPassword")

	if (err := is_password_valid(password)) is not None:
		failed_validations["password"] = err
		
	if password != confirm_password:
		failed_validations["confirmPassword"] = "Passwords do not match"
		
	role: str | None = data.get("role")
	if (err := is_role_valid(role)) is not None:
		failed_validations["role"] = err
	
	disp_name: str | None = data.get("dispName")
	if (err := is_disp_name_valid(disp_name)) is not None:
		failed_validations["dispName"] = err

	if len(failed_validations.values()) > 0:
		api_abort(ErrorCode.VALIDATION_ERROR, fields=failed_validations)

	new_user: UserModel = UserModel(
		username,									# type: ignore
		generate_password_hash(password), # type: ignore
		disp_name,								# type: ignore
		UserRole[role]									# type: ignore
	)

	try:
		db.session.add(new_user)
		db.session.commit()
	except Exception as e:
		logger.error(f"Unable to create new user with {data=} due to {e=}")
		api_abort(ErrorCode.DATABASE_ERROR)

	logger.info(f"User {new_user.id}:{new_user.username} created")

	return new_user.to_dict()


def update_user(user_id: int, data: dict) -> None:
	myself: UserModel | None = get_user_from_session()
	if myself is None:
		api_abort(ErrorCode.FORBIDDEN)
	
	if myself.role != UserRole.ADMIN and user_id != myself.id:
		api_abort(ErrorCode.FORBIDDEN)

	user: UserModel | None = db.session.get(UserModel, user_id)
	if user is None:
		api_abort(ErrorCode.USER_NOT_FOUND)
	
	failed_validations: dict = {}

	current_password: str | None = data.get("currentPassword")
	new_password: str | None = data.get("newPassword")
	new_confirm_password: str | None = data.get("newConfirmPassword")
	if current_password is not None and new_password is not None and new_confirm_password is not None:		
		if not check_password_hash(user.password, current_password):
			api_abort(ErrorCode.INVALID_INPUT, detail="Current password does not match")

		if (err := is_password_valid(new_password)) is not None:
			failed_validations["newPassword"] = err
			
		if new_password != new_confirm_password:
			failed_validations["newConfirmPassword"] = "Passwords do not match"

		user.password = generate_password_hash(new_password)

	disp_name: str | None = data.get("dispName")
	if disp_name is not None:
		if (err := is_disp_name_valid(disp_name)) is not None:
			failed_validations["dispName"] = err

		user.disp_name = disp_name

	role: str | None= data.get("role")
	if role is not None:
		if (err := is_role_valid(role)) is not None:
			failed_validations["role"] = err

		if myself.role != UserRole.ADMIN:
			api_abort(ErrorCode.FORBIDDEN)

		user.role = UserRole[role]

	if len(failed_validations.values()) > 0:
		api_abort(ErrorCode.VALIDATION_ERROR, fields=failed_validations)

	try:
		db.session.commit()
	except Exception as e:
		logger.error(f"Unable to save user update with {data=} due to {e=}")
		api_abort(ErrorCode.DATABASE_ERROR)

	logger.info(f"User {user.id}:{user.username} updated")


def delete_user(user_id: int) -> None:
	user: UserModel | None = db.session.get(UserModel, user_id)
	if user is None:
		api_abort(ErrorCode.USER_NOT_FOUND)

	try:
		db.session.delete(user)
		db.session.commit()
	except Exception as e:
		logger.error(f"Unable to delete user {user_id=} due to {e=}")
		api_abort(ErrorCode.DATABASE_ERROR)

	logger.info(f"User {user_id} deleted")
