from flask_restx import Api, Namespace

ns: Namespace = Namespace("auth v1", description="Authentication operations v1", path="/1/auth")

def append_namespace(api: Api) -> None:
	# This is to trigger the import of routes
	from . import routes
 
	api.add_namespace(ns)
