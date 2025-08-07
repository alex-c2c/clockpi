from logging import Logger, getLogger
from typing import Any

from flask import session
from flask_restx import Resource

from . import ns

logger: Logger = getLogger(__name__)

"""
API
"""

@ns.route("/")
class SessionRes(Resource):
	def get(self) -> dict:
		logger.debug(f"{session=}")
		user: Any | None = session.get("user")
		res: dict = {}

		if user is None:
			res["message"] = "Missing session"
			return res, 401

		res["message"] = ""
		res["user"] = user
		return res, 200
