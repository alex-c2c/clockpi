from logging import Logger, getLogger

from flask import session
from flask_restx import Resource

from app.lib.errors import api_abort, ErrorCode
from app.user.models import UserModel

from . import ns
from .fields import *
from .logic import *

logger: Logger = getLogger(__name__)

"""
API
"""

@ns.route("")
class SessionRes(Resource):
	@ns.response(200, "Success", model=session_model)
	@ns.response(401, "Authentication Error")
	@ns.marshal_with(session_model)
	def get(self):
		user: UserModel | None = get_user_from_session()
		if user is None:
			api_abort(ErrorCode.AUTHENTICATION_FAILED)
		
		clear_session()
		init_session(user)

		return user.to_dict(), 200
