from flask import Blueprint, redirect, url_for
from flask_restx import Namespace, Resource

from app import api_v1
from app.auth.logic import login_required, apikey_or_login_required
from . import logger
from .logic import clear_clock_display, update_clock_display


bp: Blueprint = Blueprint("epd", __name__, url_prefix="/epd")
ns: Namespace = api_v1.namespace("epd", description="EPD operations")
ns_int: Namespace = api_v1.namespace("epd_int", description="EPD operations (Internal use)")


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
