from flask import Blueprint, redirect, url_for
from flask_restx import Namespace, Resource

from app import api_v1
from app.auth.logic import apikey_required, login_required
from . import logger
from .logic import clear_display, update_display


bp: Blueprint = Blueprint("epd", __name__, url_prefix="/epd")
ns: Namespace = api_v1.namespace("epd", description="EPD operations")


"""
API
"""


@ns.route("/clear")
class ClearRes(Resource):
	@apikey_required
	def get(self) -> dict:
		clear_display()
		return "", 204


@ns.route("/refresh")
class RefreshRes(Resource):
	@apikey_required
	def get(self) -> dict:
		update_display()
		return "", 204


"""
Blueprint
"""


@bp.route("/clear", methods=["GET"])
@login_required
def view_clear():
	clear_display()

	return redirect(location=url_for("main.view_test"))


@bp.route("/refresh", methods=["GET"])
@login_required
def view_refresh():
	update_display()

	return redirect(location=url_for("main.view_test"))
