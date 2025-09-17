from flask import session

from app import db
from app.lib.errors import api_abort, ErrorCode
from app.user.models import UserModel


def get_user_from_session() -> dict:
	user_id: int | None = session.get("userId")
	if user_id is None:
		api_abort(ErrorCode.AUTHENTICATION_FAILED)
		
	user: UserModel | None = db.session.get(UserModel, session.get("userId"))
	if user is None:
		api_abort(ErrorCode.AUTHENTICATION_FAILED)
		
	return user.to_dict()


def init_session(user: UserModel) -> None:
	session.clear()
	session["userId"] = user.id
	session["username"] = user.username
	session["dispName"] = user.disp_name
	session["role"] = user.role.value
	
	
def clear_session() -> None:
	session.clear()
