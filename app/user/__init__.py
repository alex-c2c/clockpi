from flask_restx import Api, Namespace

ns: Namespace = Namespace("user_v1", description="User management (ver 1)", path="/1/user")

def append_namespace(api: Api) -> None:
	# This is to trigger the import of routes
	from . import routes
 
	api.add_namespace(ns)
