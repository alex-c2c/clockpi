from flask_restx import Api, Namespace

ns: Namespace = Namespace("device_v1", description="Device operations (Ver 1)", path="/1/device")

def append_namespace(api: Api) -> None:
	# This is to trigger the import of routes
	from . import routes
 
	api.add_namespace(ns)
