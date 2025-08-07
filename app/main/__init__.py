from flask_restx import Api, Namespace

ns: Namespace = Namespace("main_v1", description="Main operations (Ver 1)", path="/1/main")

def append_namespace(api: Api) -> None:
	# This is to trigger the import of routes
	from . import routes
 
	api.add_namespace(ns)
