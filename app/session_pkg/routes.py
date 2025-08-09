from logging import Logger, getLogger
from typing import Any

from flask import session
from flask_restx import Resource

from app import db
from app.user.models import UserModel

from . import ns
from .logic import *

logger: Logger = getLogger(__name__)

"""
API
"""

@ns.route("/")
class SessionRes(Resource):
	@ns.response(200, "")
	@ns.response(401, "Authentication Error")
	def get(self):
		logger.debug(f"{session=}")
		user: UserModel | None = get_user_from_session()
		if user is None:
			ns.abort(401, "Authentication Error")
			return
		
		clear_session()
		init_session(user)

		return user.to_dict(), 200
