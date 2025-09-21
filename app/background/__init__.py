from flask_restx import Api, Namespace

ns: Namespace = Namespace("background_v1", description="Background operations (Ver 1)", path="/1/background")

def append_namespace(api: Api) -> None:
	# This is to trigger the import of routes
	from . import routes
 
	api.add_namespace(ns)
