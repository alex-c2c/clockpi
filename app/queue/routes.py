from flask import Blueprint, redirect, request, url_for
from flask_restx import Namespace, Resource

from app import api_v1
from app.auth.logic import apikey_or_login_required, login_required
from app.consts import ERR_QUEUE_INVALID_ID
from . import logger
from .logic import get_queue, shuffle_queue, move_to_first, shift_next


bp: Blueprint = Blueprint("queue", __name__, url_prefix="/queue")
ns: Namespace = api_v1.namespace("queue", description="Queue operations")

"""
API
"""


@ns.route("/")
class QueueRes(Resource):
	@apikey_or_login_required
	def get(self) -> dict:
		queue: list[int] = get_queue()
		return {"queue": queue}, 200


@ns.route("/shuffle")
class ShuffleRes(Resource):
	@apikey_or_login_required
	def get(self) -> dict:
		shuffle_queue()
		return "", 204


@ns.route("/next")
class NextRes(Resource):
	@apikey_or_login_required
	def get(self) -> dict:
		shift_next()
		return "", 204


@ns.route("/select/<int:id>")
@api_v1.doc(responses={400: "Wallpaper ID not found"}, params={"id": "Wallpaper ID"})
class SelectRes(Resource):
	@api_v1.doc(description="")
	@apikey_or_login_required
	def get(self, id):
		result: int = move_to_first(id)
		if result == 0:
			return "", 204
		elif result == ERR_QUEUE_INVALID_ID:
			return {"error": "Invalid ID"}, 400
		else:
			return {"error": "Bad request"}, 400
