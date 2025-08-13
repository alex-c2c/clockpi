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
	@ns.response(200, "List of wallpaper IDs", model=queue_fields)
	@ns.response(401, "Authentication Error")
	@ns.marshal_with(queue_fields)
	def get(self):
		queue: list[int] = get_queue_model().get_queue()
		return {"queue": queue}, 200


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
	@ns.response(404, "Missing or invalid ID")
	@ns.response(500, "Internal Server Error")
	@ns.expect(queue_select_fields, validate=True)
	def patch(self):
		data: dict = ns.payload
		move_to_first(data.get("id"))
		return "", 204
