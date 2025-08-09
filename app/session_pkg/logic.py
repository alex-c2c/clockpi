from flask import session

from app import db
from app.user.models import UserModel


def get_user_from_session() -> UserModel | None:
	return db.session.get(UserModel, session.get("id"))


def init_session(user: UserModel) -> None:
	session.clear()
	session["id"] = user.id
	session["username"] = user.username
	session["dispName"] = user.disp_name
	session["role"] = user.role
	
	
def clear_session() -> None:
	session.clear()
