from flask_restx import Resource

from app.lib.decorators import local_apikey_required

from . import ns
from .logic import next_all_queue, shuffle_all_queue, tick_all

@ns.route("/tick-all")
class TickAllRes(Resource):
	@local_apikey_required
	@ns.response(204, "Success")
	def post(self):
		
		tick_all()
		
		return "", 204


@ns.route("/next-all")
class ShiftAllRes(Resource):
	@local_apikey_required
	@ns.response(204, "Success")
	def post(self):
		
		next_all_queue()
		
		return "", 204
		
		
@ns.route("/shuffle-all")
class ShuffleAllRes(Resource):
	@local_apikey_required
	@ns.response(204, "Success")
	def post(self):
		
		shuffle_all_queue()
		
		return "", 204
