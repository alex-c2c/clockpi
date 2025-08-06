from flask_restx import Api, Namespace

ns: Namespace = Namespace("epd", description="EPD operations", path="/1/epd")

def append_namespace(api: Api) -> None:
	# This is to trigger the import of routes
	from . import routes
 
	api.add_namespace(ns)
