from flask import session
from flask_restx import Resource
from logging import Logger, getLogger

from app.lib.decorators import admin_required, login_required
from app.consts import *

from . import ns
from .fields import *
from .logic import *

logger: Logger = getLogger(__name__)


"""
API
"""


@ns.route("/<int:schedule_id>")
@ns.param("id", "Schedule ID")
class ScheduleRes(Resource):
	@admin_required
	@ns.response(204, "")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "Schedule not found")
	@ns.response(500, "Internal Server Error")
	def delete(self, schedule_id: int):
		user_id: int = session.get("id", 0)
		
		delete_schedule(user_id, schedule_id)
		
		return "", 204

	@admin_required
	@ns.response(204, "")
	@ns.response(400, "Bad Request")
	@ns.response(401, "Authentication Error")
	@ns.response(403, "Authorization Error")
	@ns.response(404, "Schedule not found")
	@ns.response(500, "Internal Server Error")
	@ns.expect(schedule_update_fields, validate=True)
	def patch(self, schedule_id: int):
		user_id: int = session.get("id", 0)
		payload = ns.payload
		
		update_schedule(user_id, schedule_id, payload)
		
		return "", 204
