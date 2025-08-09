import functools
import os
from logging import Logger, getLogger

from flask import request, session
from werkzeug.security import check_password_hash

from app.session_pkg.logic import init_session
from app.user.models import UserModel

from . import ns

logger: Logger = getLogger(__name__)

"""""
LOGIC
"""""

def login_required(func):
	@functools.wraps(func)
	def decorator(*args, **kwargs):
		if session.get("user") is None:
			res: dict = {}
			res["message"] = "Invalid session data"
			return res, 401

		return func(*args, **kwargs)

	return decorator


def local_apikey_required(func):
	@functools.wraps(func)
	def decorator(*args, **kwargs):
		local_apikey: str | None = os.environ.get("LOCAL_API_KEY")
		if os.environ.get("LOCAL_API_KEY") is None:
			return {"error": "Internal Server Error"}, 500

  		# header keys cannot contain '_'
		api_key: str | None = request.headers.get("api-key")
		if api_key is None:
			return {"error": "Please provide an API key"}, 400		

		if local_apikey != api_key:
			return {"error": "Invalid API key"}, 400

		return func(*args, **kwargs)

	return decorator


def login_user(data: dict) -> None:
	username: str = data.get("username", "")
	password: str = data.get("password", "")
	
	user: UserModel | None = UserModel.query.filter_by(username=username).one_or_none()
	if user is None:
		ns.abort(401, "Invalid username or password")
		return
		
	if not check_password_hash(user.password, password):
		ns.abort(401, "Invalid username or password")
		return
	
	init_session(user)
