from logging import Logger, getLogger
from flask import session

from app import db
from app.user.models import UserModel


logger: Logger = getLogger(__name__)


def get_user_from_session() -> UserModel | None:
	user_id: int = session.get("userId", 0)
	return db.session.get(UserModel, user_id)


def init_session(user: UserModel) -> None:
	session["userId"] = user.id
	session["username"] = user.username
	session["dispName"] = user.disp_name
	session["role"] = user.role.value
	
	
def clear_session() -> None:
	session.clear()
