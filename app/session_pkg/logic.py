from flask import session

from app.user.models import UserModel


def init_session(user: UserModel) -> None:
	session.clear()
	session["id"] = user.id
	session["username"] = user.username
	session["dispName"] = user.disp_name
	
	
def clear_session() -> None:
	session.clear()
