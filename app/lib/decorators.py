import functools
import os
from logging import Logger, getLogger

from flask import request

from app.lib.errors import api_abort, ErrorCode
from app.session_pkg.logic import get_user_from_session
from app.user.consts import UserRole
from app.user.models import UserModel


logger: Logger = getLogger(__name__)


def login_required(func):
	@functools.wraps(func)
	def decorator(*args, **kwargs):
		user: UserModel | None = get_user_from_session()
		if user is None:
			api_abort(ErrorCode.AUTHENTICATION_FAILED)
			
		return func(*args, **kwargs)

	return decorator

	
def admin_required(func):
	@functools.wraps(func)
	def decorator(*args, **kwargs):
		user: UserModel | None = get_user_from_session()
		if user is None:
			api_abort(ErrorCode.AUTHENTICATION_FAILED)
		
		if user.role != UserRole.ADMIN:
			api_abort(ErrorCode.FORBIDDEN)
			
		return func(*args, **kwargs)

	return decorator
	


def local_apikey_required(func):
	@functools.wraps(func)
	def decorator(*args, **kwargs):
		local_apikey: str | None = os.environ.get("LOCAL_API_KEY")
		if os.environ.get("LOCAL_API_KEY") is None:
			logger.error(f"'LOCAL_API_KEY' not found in environment")
			api_abort(ErrorCode.INSUFFICIENT_SCOPE, detail="'LOCAL_API_KEY' not found in environment")
			
  		# header keys cannot contain '_'
		api_key: str | None = request.headers.get("api-key")
		if api_key is None:
			logger.error(f"'api-key' not found in header")
			api_abort(ErrorCode.INSUFFICIENT_SCOPE, detail="'api-key' not found in header")
			
		if local_apikey != api_key:
			logger.error(f"'api-key' is invalid")
			api_abort(ErrorCode.INSUFFICIENT_SCOPE, detail="'api-key' is invalid.")
			
		return func(*args, **kwargs)

	return decorator
