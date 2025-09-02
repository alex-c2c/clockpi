import functools
import os
from logging import Logger, getLogger

from flask import request

from app import api
from app.session_pkg.logic import get_user_from_session
from app.user.consts import UserRole
from app.user.models import UserModel


logger: Logger = getLogger(__name__)


def login_required(func):
	@functools.wraps(func)
	def decorator(*args, **kwargs):
		user: UserModel | None = get_user_from_session()
		if user is None:
			api.abort(401, "Authentication Error")
			return
			
		return func(*args, **kwargs)

	return decorator

	
def admin_required(func):
	@functools.wraps(func)
	def decorator(*args, **kwargs):
		user: UserModel | None = get_user_from_session()
		if user is None:
			api.abort(401, "Authentication Error")
			return
		
		if user.role != UserRole.ADMIN:
			api.abort(403, "Authorization Error")
			return
			
		return func(*args, **kwargs)

	return decorator
	


def local_apikey_required(func):
	@functools.wraps(func)
	def decorator(*args, **kwargs):
		local_apikey: str | None = os.environ.get("LOCAL_API_KEY")
		if os.environ.get("LOCAL_API_KEY") is None:
			api.abort(500, "API key not set")
			return
			
  		# header keys cannot contain '_'
		api_key: str | None = request.headers.get("api-key")
		if api_key is None:
			api.abort(401, "API key not found")
			return
			
		if local_apikey != api_key:
			api.abort(401, "Invalid API key")
			return
			
		return func(*args, **kwargs)

	return decorator
