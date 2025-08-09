import functools
import os
from logging import Logger, getLogger

from flask import request
from werkzeug.security import check_password_hash

from app.session_pkg.logic import get_user_from_session, init_session
from app.user.consts import UserRole
from app.user.models import UserModel

from . import ns

logger: Logger = getLogger(__name__)

"""""
LOGIC
"""""

def login_required(func):
	@functools.wraps(func)
	def decorator(*args, **kwargs):
		user: UserModel | None = get_user_from_session()
		if user is None:
			ns.abort(401, "Authentication Error")
			return
			
		return func(*args, **kwargs)

	return decorator

	
def admin_required(func):
	@functools.wraps(func)
	def decorator(*args, **kwargs):
		user: UserModel | None = get_user_from_session()
		if user is None:
			ns.abort(401, "Authentication Error")
			return
		
		if user.role != UserRole.ADMIN:
			ns.abort(403, "Authorization Error")
			return
			
		return func(*args, **kwargs)

	return decorator
	


def local_apikey_required(func):
	@functools.wraps(func)
	def decorator(*args, **kwargs):
		local_apikey: str | None = os.environ.get("LOCAL_API_KEY")
		if os.environ.get("LOCAL_API_KEY") is None:
			ns.abort(500, "API key not set")
			return
			
  		# header keys cannot contain '_'
		api_key: str | None = request.headers.get("api-key")
		if api_key is None:
			ns.abort(401, "API key not found")
			return
			
		if local_apikey != api_key:
			ns.abort(401, "Invalid API key")
			return
			
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
