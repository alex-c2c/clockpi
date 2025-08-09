from flask_restx import Resource

from app import api
from app.auth.logic import local_apikey_required, login_required
from app.consts import ERR_QUEUE_INVALID_ID

from . import ns
from .logic import get_queue, shuffle_queue, move_to_first, shift_next


"""
API
"""


@ns.route("/")
class QueueRes(Resource):
	@local_apikey_required
	def get(self):
		queue: list[int] = get_queue()
		return {"queue": queue}, 200


@ns.route("/shuffle")
class ShuffleRes(Resource):
	@local_apikey_required
	def get(self):
		shuffle_queue()
		return "", 204


@ns.route("/next")
class NextRes(Resource):
	@local_apikey_required
	def get(self):
		shift_next()
		return "", 204


@ns.route("/select/<int:id>")
@api.doc(responses={400: "Wallpaper ID not found"}, params={"id": "Wallpaper ID"})
class SelectRes(Resource):
	@api.doc(description="")
	@login_required
	def get(self, id):
		result: int = move_to_first(id)
		if result == 0:
			return "", 204
		elif result == ERR_QUEUE_INVALID_ID:
			return {"error": "Invalid ID"}, 400
		else:
			return {"error": "Bad request"}, 400
