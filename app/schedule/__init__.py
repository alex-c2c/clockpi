from logging import Logger, getLogger

from flask_restx import Api, Namespace

ns: Namespace = Namespace("schedule_v1", description="Scheduling operations (Ver 1)", path="/1/schedule")

logger: Logger = getLogger(__name__)

def append_namespace(api: Api) -> None:
	# This is to trigger the import of routes
	from . import routes

	api.add_namespace(ns)
