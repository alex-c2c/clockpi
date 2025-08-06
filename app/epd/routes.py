from logging import Logger, getLogger

from flask_restx import Resource

from app.auth.logic import apikey_or_login_required

from . import ns
from .logic import clear_clock_display, update_clock_display

logger: Logger = getLogger(__name__)


"""
API
"""


@ns.route("/clear")
class ClearRes(Resource):
	@apikey_or_login_required
	def get(self) -> dict:
		clear_clock_display()
		return "", 204


@ns.route("/refresh")
class RefreshRes(Resource):
	@apikey_or_login_required
	def get(self) -> dict:
		update_clock_display()
		return "", 204
