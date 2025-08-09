import functools
import os
import re
from logging import Logger, getLogger

from app.user.models import UserModel

from .consts import *

from app import db

logger: Logger = getLogger(__name__)

"""""
LOGIC
"""""

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
