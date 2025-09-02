from logging import Logger, getLogger

from flask_restx import Resource

from app.lib.decorators import login_required

from . import ns
from .logic import clear_clock_display, save_current_to_temp, update_clock_display

logger: Logger = getLogger(__name__)


"""
API
"""


@ns.route("/clear")
class ClearRes(Resource):
	@login_required
	def get(self):
		clear_clock_display()
		return "", 204


@ns.route("/refresh")
class RefreshRes(Resource):
	@login_required
	def get(self):
		update_clock_display()
		return "", 204


@ns.route("/save-current")
class SaveCurrentToTempRes(Resource):
	@login_required
	def get(self):
		save_current_to_temp()
		return "", 204
