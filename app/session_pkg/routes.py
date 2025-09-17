from logging import Logger, getLogger

from flask_restx import Resource

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
		user: dict = get_user_from_session()
		
		return user, 200
