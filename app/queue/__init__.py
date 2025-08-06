from flask_restx import Api, Namespace

ns: Namespace = Namespace("queue", description="Queue operations", path="/1/queue")

def append_namespace(api: Api) -> None:
	# This is to trigger the import of routes
	from . import routes
 
	api.add_namespace(ns)
