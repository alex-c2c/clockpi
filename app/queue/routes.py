from flask_restx import Resource

from app import api
from app.lib.decorators import admin_required, login_required

from . import ns
from .fields import *
from .logic import *


"""
API
"""


@ns.route("")
class QueueRes(Resource):
	@login_required
	@ns.response(200, "", model=[int])
	@ns.response(401, "Authentication Error")
	def get(self):
		queue: list[int] = get_queue_model().get_queue()
		return queue, 200


@ns.route("/shuffle")
class ShuffleRes(Resource):
	@admin_required
	@ns.response(204, "")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(500, "Internal Server Error")
	def get(self):
		shuffle_queue()
		return "", 204


@ns.route("/next")
class NextRes(Resource):
	@admin_required
	@ns.response(204, "")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(500, "Internal Server Error")
	def get(self):
		shift_next()
		return "", 204


@ns.route("/select")
class SelectRes(Resource):
	@admin_required
	@ns.response(204, "")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "ID not found")
	@ns.response(500, "Internal Server Error")
	@ns.expect(queue_select_fields, validate=True)
	def patch(self):
		data: dict = ns.payload
		move_to_first(data.get("id"))
		return "", 204
