from flask_restx import Resource

from app import api
from app.auth.logic import admin_required, local_apikey_required, login_required

from . import ns
from .fields import *
from .logic import *


"""
API
"""


@ns.route("/")
class QueueRes(Resource):
	@login_required
	@ns.response(200, queue_model)
	@ns.response(401, "Authentication Error")
	@ns.marshal_with(queue_model)
	def get(self):
		queue: list[int] = get_queue_model().get_queue()
		return {"queue": queue}, 200


@ns.route("/shuffle")
class ShuffleRes(Resource):
	@login_required
	@ns.response(204, "")
	@ns.response(400, "Bad Request")
	@ns.response(401, "Authentication Error")
	@ns.response(404, "Missing or invalid ID")
	@ns.response(500, "Server error occured")
	def get(self):
		shuffle_queue()
		return "", 204


@ns.route("/next")
class NextRes(Resource):
	@login_required
	@ns.response(204, "")
	@ns.response(400, "Bad Request")
	@ns.response(401, "Authentication Error")
	@ns.response(404, "Missing or invalid ID")
	@ns.response(500, "Server error occured")
	def get(self):
		shift_next()
		return "", 204


@ns.route("/select")
class SelectRes(Resource):
	@admin_required
	@ns.response(204, "")
	@ns.response(400, "Bad Request")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "Missing or invalid ID")
	@ns.response(500, "Server error occured")
	@ns.expect(queue_select_model, validate=True)
	def patch(self):
		data = ns.payload
		move_to_first(data.get("id"))
		return "", 204
