from logging import Logger, getLogger

from flask_restx import Resource

from app.lib.errors import ErrorCode, api_abort
from app.user.fields import user_fields

from . import ns
from .logic import *

logger: Logger = getLogger(__name__)

"""
API
"""

@ns.route("")
class SessionRes(Resource):
	@ns.response(200, "Success", model=user_fields)
	@ns.marshal_with(user_fields)
	def get(self):
		user: UserModel | None = get_user_from_session()
		
		if user is None:
			api_abort(ErrorCode.FORBIDDEN)
		
		return user.to_dict(), 200
