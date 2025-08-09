from logging import Logger, getLogger

from flask_restx import Resource

from app.auth.logic import local_apikey_required

from . import ns
from .logic import clear_clock_display, update_clock_display

logger: Logger = getLogger(__name__)


"""
API
"""


@ns.route("/clear")
class ClearRes(Resource):
	@local_apikey_required
	def get(self):
		clear_clock_display()
		return "", 204


@ns.route("/refresh")
class RefreshRes(Resource):
	@local_apikey_required
	def get(self):
		update_clock_display()
		return "", 204
